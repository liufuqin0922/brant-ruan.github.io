---
title: 打印店病毒分析 - Mydocuments.exe
category: Sec
---

## 打印店病毒分析 - Mydocuments.exe

样本仅供学习研究使用：

- [脱壳前]({{ site.url }}/resources/printer-virus/virus-1/mydocument.exe.en.b64)
- [脱壳后]({{ site.url }}/resources/printer-virus/virus-1/mydocument-unshell.exe.en.b64)

---

### 基本信息

运行明显特征：把U盘中正常文件隐藏放入 MyDocuments 文件夹中，该文件夹为隐藏+系统文件属性。同时产生一个MyDocument.exe，文件夹图标的病毒本体。用户不注意就会运行病毒。

VirSCAN.org在线测试：

脱壳前：

Scanner results:71%Scanner(s) (28/39)found malware  
File Name      : mydocument.exe  
File Size      : 28160 byte  
File Type      : application/x-dosexec  
MD5            : e4f4a55051884d42595a6be92e4f582f  
SHA1           : a4e8ea5b7180455eb0dd0f58fd59ef224a376827  
[Online report](http://r.virscan.org/report/7d3d08b86ffe374f1ab07ba81b1b80cb)  
PACKER : UPX 0.89.6 - 1.02 / 1.05 - 1.24 -> Markus & Laszlo  
Sub-file : upx_c_9400bb61dumpFile / 70ffdb68b8c7f260c794f0180c0683c8 / EXE

脱壳后：

Scanner results:41%Scanner(s) (16/39)found malware  
File Name      : virus.exe  
File Size      : 57344 byte  
File Type      : application/x-dosexec  
MD5            : ca4aac12de7f90e7f5788940ae616d92  
SHA1           : 6727479086fd2ffbd2572e6e650adfe04d80b286  
[Online report](http://r.virscan.org/report/f4342882fa7427c3031bfcc42867d411)

有点意思，脱壳后反而查出率降低了不少。

### 静态分析

IDA初步分析程序为Windows 32位程序，EP注明UPX，似乎有UPX加壳。  
使用PEID查壳，并从网上下载了脱壳机脱壳。（这里挖个坑，以后尝试手动脱这个壳）  
经脱壳，原28KB程序变为58KB。

