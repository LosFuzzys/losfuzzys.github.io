---
layout: post
title: "justCTF 2020: Remote Password Manager"
author: hweissi
categories: writeup
tags: [cat/forensics, cat/misc, tool/volatility]
---

* **Category:** forensics, misc
* **Description:**

> I just have the safest password manager. Even if you gonna steal my laptop, you won't be able to get my secrets.
>
> https://ams3.digitaloceanspaces.com/justctf/69f7647d-2f7a-4604-b9f6-553c6bb447ee/challenge.tar.gz (~357MB)
>
> Alternative download URL: https://drive.google.com/file/d/10j7WqRzx2Ytc5_NU1yewo6Czq8Akb0Xy/
>
> Hints:
>
>Remote does not necessarily mean browser access, look closer
>In case of wondering if the downloaded/untared file is corrupted:
>$ md5sum challenge.vmem   
>c0944ccb2f44ec1d6087a5ec42f3aa01  challenge.vmem
> 

## Writeup

The challenge contains `challenge.vmem`, which is a memory dump of a windows machine.

I used Volatility to analyze the memory dump.

With `vol.py -f challenge.vmem imageinfo`, we find out that we should use the Win10x64_18362 profile for this dump.

Now we can analyze the memory dump. 

Using `vol.py -f challenge.vmem --profile=Win10x64_18362 pslist` we can get a list of running processes:

```
Volatility Foundation Volatility Framework 2.6.1
Offset(V)          Name                    PID   PPID   Thds     Hnds   Sess  Wow64 Start                          Exit                          
------------------ -------------------- ------ ------ ------ -------- ------ ------ ------------------------------ ------------------------------
0xffffe00d93088040 System                    4      0    198        0 ------      0 2021-01-18 13:50:29 UTC+0000                                 
0xffffe00d930d6080 Registry                136      4      4        0 ------      0 2021-01-18 13:50:25 UTC+0000                                 
0xffffe00d976dd040 smss.exe                408      4      4        0 ------      0 2021-01-18 13:50:29 UTC+0000                                 
0xffffe00d97d1d140 csrss.exe               528    520     12        0      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98610080 wininit.exe             608    520      5 --------      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d97d43080 csrss.exe               616    600     13        0      1      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98687200 services.exe            692    608     10        0      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d986c0080 winlogon.exe            724    600      5        0      1      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98522080 lsass.exe               780    608     12        0      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98e633c0 svchost.exe             904    692     28        0      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98e842c0 fontdrvhost.ex          932    608      6        0      0      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98e822c0 fontdrvhost.ex          940    724      6        0      1      0 2021-01-18 13:50:30 UTC+0000                                 
0xffffe00d98ecb440 svchost.exe            1020    692     18        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98f810c0 dwm.exe                 604    724     24        0      1      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98fc63c0 svchost.exe            1048    692     80        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98fe8440 svchost.exe            1088    692     36        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98fea480 svchost.exe            1096    692     21        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98fec480 svchost.exe            1104    692      6        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98fe9080 svchost.exe            1116    692     19        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d98745400 svchost.exe            1192    692     13        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d987f9400 svchost.exe            1456    692      4        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d99067440 svchost.exe            1564    692      7        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d987f8080 svchost.exe            1644    692     34        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d9906a040 MemCompression         1668      4     47 -------- ------      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d992a3480 svchost.exe            1944    692     13        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d93085080 svchost.exe            2036    692      5        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d99332480 svchost.exe            2044    692     15        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d930cc080 svchost.exe            1748    692     11        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d97a50080 spoolsv.exe            2128    692     15        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d993d1480 svchost.exe            2200    692     23        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d994e23c0 svchost.exe            2440    692     10        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d994e7440 vmtoolsd.exe           2448    692     12        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d994e9480 VGAuthService.         2456    692      3        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d995044c0 MsMpEng.exe            2520    692     45        0      0      0 2021-01-18 13:50:31 UTC+0000                                 
0xffffe00d9959e3c0 svchost.exe            2640    692     16        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d996d9400 dllhost.exe            2900    692     27        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d9978d400 dllhost.exe            2256    692     17        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d998083c0 svchost.exe            1600    692      6        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d99884400 WmiPrvSE.exe           2528    904     15        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d998ed440 msdtc.exe              3132    692     13        0      0      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d99999080 sihost.exe             3308   1048     15        0      1      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d999dd080 svchost.exe            3344    692     15        0      1      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d99a7e480 taskhostw.exe          3492   1048     11        0      1      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d99bf20c0 ctfmon.exe             3764   1192     12        0      1      0 2021-01-18 13:50:32 UTC+0000                                 
0xffffe00d99be04c0 userinit.exe           3844    724      0 --------      1      0 2021-01-18 13:50:32 UTC+0000   2021-01-18 13:50:56 UTC+0000  
0xffffe00d99ceb4c0 explorer.exe           3904   3844     66        0      1      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d99f2d440 svchost.exe             504    692      8        0      1      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d99faf080 dllhost.exe            4220    904      6        0      1      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d9a015080 StartMenuExper         4436    904     59        0      1      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d9a07f3c0 VSSVC.exe              4620    692      5        0      0      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d9a10f440 RuntimeBroker.         4692    904      8        0      1      0 2021-01-18 13:50:33 UTC+0000                                 
0xffffe00d9a1de400 SearchIndexer.         4808    692     56        0      0      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a1e1080 SearchUI.exe           4848    904     40        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a251440 RuntimeBroker.         5108    904     15        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a316240 backgroundTask         5136    904     14        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a5a9240 ApplicationFra         5156    904     19        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a5ba0c0 MicrosoftEdge.         5196    904     47        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a6f84c0 NisSrv.exe             5356    692     11        0      0      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a34c480 browser_broker         5576    904     12        0      1      0 2021-01-18 13:50:34 UTC+0000                                 
0xffffe00d9a815440 RuntimeBroker.         5788    904      5        0      1      0 2021-01-18 13:50:35 UTC+0000                                 
0xffffe00d9a818440 RuntimeBroker.         5852    904     15        0      1      0 2021-01-18 13:50:35 UTC+0000                                 
0xffffe00d9a81b080 MicrosoftEdgeC         5864    904     74        0      1      0 2021-01-18 13:50:35 UTC+0000                                 
0xffffe00d9a89f080 MicrosoftEdgeS         5968   5852     12        0      1      0 2021-01-18 13:50:35 UTC+0000                                 
0xffffe00d99f74440 smartscreen.ex         6504    904     19        0      1      0 2021-01-18 13:50:45 UTC+0000                                 
0xffffe00d9a7a34c0 SecurityHealth         6560   3904      4        0      1      0 2021-01-18 13:50:45 UTC+0000                                 
0xffffe00d9a9c1080 SecurityHealth         6596    692     13        0      0      0 2021-01-18 13:50:45 UTC+0000                                 
0xffffe00d9a4b64c0 vm3dservice.ex         6676   3904      1        0      1      0 2021-01-18 13:50:46 UTC+0000                                 
0xffffe00d9a4b5080 vmtoolsd.exe           6696   3904      9        0      1      0 2021-01-18 13:50:46 UTC+0000                                 
0xffffe00d9a4b7080 OneDrive.exe           6752   3904     24        0      1      1 2021-01-18 13:50:47 UTC+0000                                 
0xffffe00d934064c0 dllhost.exe            7000    904     14        0      1      0 2021-01-18 13:50:50 UTC+0000                                 
0xffffe00d9af06400 WmiPrvSE.exe           2488    904     16        0      0      0 2021-01-18 13:50:52 UTC+0000                                 
0xffffe00d9af0f480 svchost.exe            4044    692     13        0      0      0 2021-01-18 13:50:52 UTC+0000                                 
0xffffe00d9af57080 mstsc.exe              6484   3904     27        0      1      0 2021-01-18 13:50:54 UTC+0000                                 
0xffffe00d9afd2080 svchost.exe            6832    692      9        0      0      0 2021-01-18 13:50:56 UTC+0000                                 
0xffffe00d9b0693c0 WmiApSrv.exe           6928    692      8        0      0      0 2021-01-18 13:50:57 UTC+0000                                 
0xffffe00d9ae87080 audiodg.exe            7792   1944      8        0      0      0 2021-01-18 13:51:04 UTC+0000                                 
0xffffe00d9a24a4c0 MicrosoftEdgeC         8104    904     19        0      1      0 2021-01-18 13:51:11 UTC+0000                                 
0xffffe00d9b6454c0 MicrosoftEdgeC         7636    904     43        0      1      0 2021-01-18 13:51:21 UTC+0000                                 
0xffffe00d9b1c14c0 MicrosoftEdgeC         7532    904     20        0      1      0 2021-01-18 13:51:21 UTC+0000                                 
0xffffe00d9340f080 cmd.exe                7420   2448      0 --------      0      0 2021-01-18 13:51:49 UTC+0000   2021-01-18 13:51:49 UTC+0000  
0xffffe00d930d0080 conhost.exe            8024   7420      0        0      0      0 2021-01-18 13:51:49 UTC+0000 

```

On first glance there is nothing out of the ordinary here.

Here's where the clues of the challenge come in:

From the name *Remote* Password Manager, we can assume that it's probably accessed somehow over the network.
Then, there's this tip:

> Remote does not necessarily mean browser access, look closer

So we can probably ignore the browser.

One other remote tool that is running here is `mstsc.exe`, which is the Windows remote desktop connection.

We can dump its memory with `vol.py -f challenge.vmem --profile=Win10x64_18362 procdump -p 6484 --dump-dir procdump_mstsc`, which writes the dump to the directory we specified.
After this, I spent some time looking over the strings in this dump to maybe find something useful.
I found some suspicious things, like KeePass Passwordmanager, mentioned in the dump, but couldn't figure out how to get anywhere from there.

Then, I decided to look for image data.
I just opened the process dump as `Raw image data`. We can now scroll around the file using the `offset`-slider until we see something that looks like it might be an image:


![suspicious data](/images/posts/2021-01-30-justctf-remote-password-manager-1.png)

Now we can (carefully, so GIMP doesn't crash) adjust the width until we get a clearer picture.
We can now scroll around and play with the options until we get a readable image.
The flag is displayed in an open editor.

![flag image](/images/posts/2021-01-30-justctf-remote-password-manager-2.png)

