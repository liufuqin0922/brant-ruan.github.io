U盘在打印店感染的病毒，然而近日去U盘里找时已经没有了，似乎被360干掉了。幸好360带有隔离区，终于让我获得了样本来研究学习一下。

---

运行明显特征：把U盘中正常文件隐藏放入MyDocuments文件夹中，该文件夹为隐藏+系统文件属性。同时产生一个MyDocument.exe，文件夹图标的病毒本体。

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

![virus-1-result-1](/static/images/virus-1-result-2.png)  
![virus-1-result-1](/static/images/virus-1-result-3.png)

![virus-1-behavior](/static/images/virus-1-behavior.png)

脱壳后：

Scanner results:41%Scanner(s) (16/39)found malware  
File Name      : virus.exe  
File Size      : 57344 byte  
File Type      : application/x-dosexec  
MD5            : ca4aac12de7f90e7f5788940ae616d92  
SHA1           : 6727479086fd2ffbd2572e6e650adfe04d80b286  
[Online report](http://r.virscan.org/report/f4342882fa7427c3031bfcc42867d411)
         
![virus-1-result-1](/static/images/virus-1-result-0.png)  
![virus-1-result-1](/static/images/virus-1-result-1.png)

有点意思，脱壳后反而查出率降低了不少。

IDA初步分析： 程序为Windows 32位程序，EP注明UPX，似乎有UPX加壳。  
使用PEID查壳，从网上下载了脱壳机脱壳。（这里挖个坑，以后尝试手动脱这个壳）  
经脱壳，原28KB程序变为58KB。

IDA反编译分析：
