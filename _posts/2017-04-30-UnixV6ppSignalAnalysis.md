---
title: Unix v6-plus-plus IPC Analysis | Signal
category: CS
---

## Unix v6-plus-plus IPC Analysis | Signal

> In this part, we focus on the relationship between signal and system call.

### 0x01 Basic Knowledge

**Variables related to signal**

```
/* Current signal -- index of u_signal */
int Process::p_sig;
/* Signal handler table */
unsigned long User::u_signal[NSIG];
/* Whether signal interrupts system call: 1 yes - 0 no */
bool User::u_intflg;
/* To jump back to Trap() from Sleep(), signal received */
unsigned long User::u_qsav[2]
```

For `u_signal` we should know:  

- If `u_signal[p_sig]` is 0, then exit itself
- If `u_signal[p_sig]` is odd, then ignore this signal
- If `u_signal[p_sig]` is even, then it is handler address

**Methods related to signal**

- Send signal to current process

```
void Process::PSignal(int signal)
{
	if ( signal >= User::NSIG ) // no more space
		return;
   	if ( this->p_sig != User::SIGKILL )
		this->p_sig = signal;
	if ( this->p_pri > ProcessManager::PUSER )
		this->p_pri	= ProcessManager::PUSER;
	if ( this->p_stat == Process::SWAIT ) // wake it
		this->SetRun();
}
```

- Handle signal received

```
void Process:PSig(struct pt_context *pContext)
{
	User& u = Kernel::Instance().GetUser();
	int signal = this->p_sig;
	this->p_sig = 0;
	if ( u.u_signal[signal] != 0 )
	{
		u.u_error = User::NOERROR;
		unsigned int old_eip = pContext->eip;
		pContext->eip = u.u_signal[signal];
		pContext->esp -= 4;
		int* pInt = (int *)pContext->esp;
		*pInt = old_eip;
		u.u_signal[signal] = 0;
		return;
	}
	u.u_procp->Exit();
}
```

- Set user's signal handler

```
void Process::Ssig()
{
	User& u = Kernel::Instance().GetUser();
	int signalIndex = u.u_arg[0];
	unsigned long func = u.u_arg[1];
	if ( signalIndex <= 0 || signalIndex >= User::NSIG || signalIndex == User::SIGKILL )
		u.u_error = User::EINVAL;
		return;
	}
	u.u_ar0[User::EAX] = u.u_signal[signalIndex];
	u.u_signal[signalIndex] = func;
	if ( u.u_procp->p_sig == signalIndex )
		u.u_procp->p_sig = 0;
}
```

- Check whether signal is received

```
int Process::IsSig()
{
	User& u = Kernel::Instance().GetUser();
	if ( this->p_sig == 0 )
		return 0;
	else if ((u.u_signal[this->p_sig] & 1) == 0)
		return this->p_sig;
	return 0;
}
```

### 0x02 Dive into System Call

We will go in logic order. The number in each sub-title below is used to show function layers relationship.

To obtain an integratal view, we will take two examples with different sleep priorities and different responses to signal as a result:

- `SystemCall::Sys_Read`
- `SystemCall::Sys_Wait`

**0 | Into `SystemCall::SystemCallEntrance`**

```
SaveContext();
SwitchToKernel();
CallHandler(SystemCall, Trap);
```

Save almost all the registers.  
Then switch to kernel mode.  
Finally call `SystemCall`'s `Trap`.

**1 | Into `SystemCall::Trap`**

If process receives signal then response:

```
if ( u.u_procp->IsSig() )
{
    u.u_procp->PSig(context);
    u.u_error = User::EINTR;
    regs->eax = -u.u_error;
    return;
}
```

Then it calls `Trap1` to deal with signal:

```
Trap1(callp->call);
```

**2 | Into `SystemCall::Trap1`**

Set `u_intflg` to 1, assuming that the system call will be interrupted by signal.

```
u.u_intflg = 1;
```

Then save `esp` and `ebp` to `u_qsav`:

```
SaveU(u.u_qsav);
```

![]({{ site.url }}/resources/pictures/unixv6pp-SaveU.png)

Then call the handler function:

```
func();
```

Firstly, let's explore `SystemCall::Sys_Read`.

**3 | Into `SystemCall::Sys_Read`**

```
fileMgr.Read();
```

**4 | Into `FileManager::Read`**

```
this->Rdwr(File::FREAD);
```

**5 | Into `FileManager::Rdwr`**

```
pFile->f_inode->ReadI();
```

**6 | Into `Inode::ReadI`**

```
pBuf = bufMgr.Bread(dev, bn);
```

**7 | Into `BufferManager::Bread`**

```
this->IOWait(bp);
```

**8 | Into `BufferManager::IOWait`**

```
u.u_procp->Sleep((unsigned long)bp, ProcessManager::PRIBIO);
```

Note that `priority number < 0` means high priority sleep, and `priority number > 0` means low. Here it is `PRIBIO = -50`, so this is high priority sleep.

**9 | Into `Process::Sleep`**

```
else // high priority sleep
{
    X86Assembly::CLI();
    this->p_wchan = chan;
    this->p_stat = Process::SSLEEP;
    this->p_pri = pri;
    X86Assembly::STI();
    Kernel::Instance().GetProcessManager().Swtch();
}
```

You can see that high priority sleep will **not** be interrupted by signal.

Now it's time to go back.

**8 | Back to `BufferManager::IOWait`**  
**7 | Back to `BufferManger::Bread`**  
**6 | Back to `Inode::ReadI`**  
**5 | Back to `FileManager::Rdwr`**  
**4 | Back to `FileManager::Read`**  
**3 | Back to `SystemCall::Sys_Read`**  
**2 | Back to `SystemCall::Trap1`**

Remember that we set `u_intflg` to 1 before? If logic stream goes here, it means the system call finished successfully. So we should reset this flag variable.

```
u.u_intflg = 0;
```

**1 | Back to `SystemCall::Trap`**

```
if ( u.u_intflg != 0 )
    u.u_error = User::EINTR;
```

Here `u.u_intflg` is 0.

Then

```
if( User::NOERROR != u.u_error ){
    regs->eax = -u.u_error;
    Diagnose::Write("regs->eax = %d , u.u_error = %d\n",regs->eax,u.u_error);
}
```

At the end of `Trap`, it will check signal **again**:

```
if ( u.u_procp->IsSig() )
    u.u_procp->PSig(context);
```

**0 | Back to `SystemCall::SystemCallEntrance`**

At last, the entrance method will do some process schedule operation, which has little thing to do with signal:

```
struct pt_context *context;
__asm__ __volatile__ ("	movl %%ebp, %0; addl $0x4, %0 " : "+m" (context) );
if( context->xcs & USER_MODE ){
    while(true){
        X86Assembly::CLI();
        if(Kernel::Instance().GetProcessManager().RunRun > 0){
            X86Assembly::STI();
            Kernel::Instance().GetProcessManager().Swtch();
        }
        else
            break;
    }
}
RestoreContext();
Leave();
InterruptReturn();
```

Second, let's explore `SystemCall::Sys_Wait`. We will directly go from **function layer 3**.

**3 | Into `SystemCall::Sys_Wait`**

```
procMgr.Wait();
```

**4 | Into `ProcessManager::Wait`**

```
if (true == hasChild)
{
    u.u_procp->Sleep((unsigned long)u.u_procp, ProcessManager::PWAIT);
    continue;
}
```

Note that `PWAIT` is 40 > 0, so this is a low priority sleep.

**5 | Into ``Process:Sleep``**

```
if ( pri > 0 ) // low priority
{
    if ( this->IsSig() )
    {
        aRetU(u.u_qsav);
        return;
    }
```

![]({{ site.url }}/resources/pictures/unixv6pp-aRetU.png)

This is the difference from high priority sleep. This `Sleep` will directly skip to `Trap1`'s stack frame and then return immediately if signal received.

Code below is to switch to another process.

```
    X86Assembly::CLI();
    this->p_wchan = chan;
    this->p_stat = Process::SWAIT;
    this->p_pri = pri;
    X86Assembly::STI();
    if ( procMgr.RunIn != 0 )
    {
        procMgr.RunIn = 0;
        procMgr.WakeUpAll((unsigned long)&procMgr.RunIn);
    }
    Kernel::Instance().GetProcessManager().Swtch();
```

After waking up, check signal immediately and return `Trap` if signal received.

```
    if ( this->IsSig() )
    {
        aRetU(u.u_qsav);
        return;
    }
```

**If return to `Trap` directly:**

**1 | Back to `SystemCall::Trap`**

```
if ( u.u_intflg != 0 )
    u.u_error = User::EINTR;
```

Because `Trap1` is skipped, so `u.u_intflg` is 1.

**If no signal received during system call:**

**4 | Back to `ProcessManager::Wait`**  
**3 | Back to `SystemCall::Sys_Wait`**

And then back to 2,1 as the description of `Sys_Read`.
