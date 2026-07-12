# Windows 本地安装 Unlimited OCR：新手一步一步教程

这篇教程适合不熟悉命令行、模型和编程的普通 Windows 用户。

你不需要理解每个参数是什么意思。只要按照下面的顺序操作，并把文件放到指定位置，最后复制一整行命令即可。

本文统一使用下面两个位置：

- 模型放在：`D:\Unlimited-OCR`
- 运行程序放在：`D:\llama.cpp`

> 如果你的电脑没有 D 盘，也可以使用 C 盘，但需要把本文命令里的所有 `D:` 改成 `C:`。为了避免改错，建议有 D 盘的用户直接照本文操作。

---

## 第一步：在 D 盘新建两个文件夹

1. 按键盘上的 `Win + E`，打开“文件资源管理器”。
2. 在左边点击“此电脑”。
3. 双击打开“本地磁盘 (D:)”。
4. 在空白处点击鼠标右键。
5. 点击“新建”。
6. 点击“文件夹”。
7. 把文件夹命名为：

```text
Unlimited-OCR
```

8. 再新建一个文件夹，命名为：

```text
llama.cpp
```

完成后，D 盘里应该能看到这两个文件夹：

```text
D:\Unlimited-OCR
D:\llama.cpp
```

---

## 第二步：从 ModelScope 下载两个模型文件

### 1. 打开模型下载页面

复制下面的网址，粘贴到浏览器地址栏，然后按回车：

<https://www.modelscope.cn/models/DevQuasar/baidu.Unlimited-OCR-GGUF/files>

如果网页要求登录，请按照页面提示注册或登录 ModelScope 账号。

### 2. 下载模型本体

在文件列表中找到：

```text
baidu.Unlimited-OCR.Q8_0.gguf
```

点击它右边的“下载”按钮。

这个文件比较大，下载需要一些时间。下载过程中不要关闭浏览器。

### 3. 下载图片识别所需文件

在同一个页面中找到：

```text
mmproj-baidu.Unlimited-OCR.f16.gguf
```

同样点击文件名或右边的“下载”按钮。

这个文件不能省略。没有它，程序就不能正常读取图片。

### 4. 把两个文件放到指定文件夹

下载完成后：

1. 按 `Win + E` 打开文件资源管理器。
2. 点击左边的“下载”。
3. 找到刚刚下载的两个文件。
4. 同时选中这两个文件。
5. 点击鼠标右键，选择“剪切”。
6. 打开：

```text
D:\Unlimited-OCR
```

7. 在空白处点击鼠标右键，选择“粘贴”。

最后打开 `D:\Unlimited-OCR`，确认里面有下面两个文件：

```text
baidu.Unlimited-OCR.Q8_0.gguf
mmproj-baidu.Unlimited-OCR.f16.gguf
```

请特别检查文件名，不要让文件名末尾出现 `(1)`。

例如下面这种文件名就不对：

```text
Unlimited-OCR-BF16 (1).gguf
```

如果出现了 `(1)`，请删除多余的重复文件，或者把文件名改回本文给出的名称。

---

## 第三步：从 GitHub 下载 llama.cpp

### 1. 打开下载页面

复制下面的网址，粘贴到浏览器地址栏，然后按回车：

<https://github.com/ggml-org/llama.cpp/releases>

页面最上面的版本通常会带有绿色的 `Latest` 标记，表示这是当前最新版。

### 2. 找到下载文件的位置

向下滚动，找到 `Assets`。

如果只看到一行 `Assets`，没有看到很多文件名，请点击一下 `Assets`，文件列表就会展开。

不要下载下面这两个文件：

```text
Source code (zip)
Source code (tar.gz)
```

它们是给开发人员使用的，不是我们需要的可直接运行版本。

### 3. 根据电脑情况选择下载版本

#### 情况 A：你的电脑有 NVIDIA 显卡

NVIDIA 显卡常见名称包括：

```text
GeForce GTX
GeForce RTX
NVIDIA
```

在 `Assets` 中找到名称里同时带有以下文字的压缩包：

```text
win
cuda-12
x64
```

文件名通常类似：

```text
llama-某个版本号-bin-win-cuda-12.4-x64.zip
```

点击它进行下载。

在同一个版本的文件列表中，还需要下载 CUDA 运行文件，名称通常类似：

```text
cudart-llama-bin-win-cuda-12.4-x64.zip
```

因此，NVIDIA 显卡用户通常需要下载两个 ZIP 压缩包。

> 文件名中的版本号会不断变化。不要强行寻找和本文完全相同的版本号，只要选择页面最上方最新版中带有 `Windows x64 (CUDA 12)` 的文件即可。

#### 情况 B：没有 NVIDIA 显卡，或者不知道自己是什么显卡

请选择页面中的：

```text
Windows x64 (CPU)
```

下载的文件名通常类似：

```text
llama-某个版本号-bin-win-cpu-x64.zip
```

CPU 版本速度可能较慢，但选择起来最简单，也不会因为显卡类型选错版本。

### 4. 把 ZIP 压缩包解压到指定位置

下载完成后：

1. 按 `Win + E` 打开文件资源管理器。
2. 点击左边的“下载”。
3. 找到刚刚下载的 ZIP 压缩包。
4. 点击鼠标右键。
5. 点击“全部解压缩”。

解压完成后，打开解压出来的文件夹。

在里面找到：

```text
llama-server.exe
```

然后按下面的方法复制文件：

1. 在解压后的文件夹中按 `Ctrl + A`，选中里面的所有文件。
2. 按 `Ctrl + C` 复制。
3. 打开：

```text
D:\llama.cpp
```

4. 按 `Ctrl + V` 粘贴。

不要只复制 `llama-server.exe` 一个文件。它旁边的其他文件也可能是运行时需要的，所以要把压缩包里的全部文件一起复制过去。

#### NVIDIA 用户还要做一次

如果你下载了第二个 CUDA 运行文件：

```text
cudart-llama-bin-win-cuda-12.4-x64.zip
```

也把它解压，然后把里面的所有文件复制到：

```text
D:\llama.cpp
```

如果 Windows 提示“目标位置已有同名文件”，选择：

```text
替换目标中的文件
```

### 5. 检查文件是否放对

打开：

```text
D:\llama.cpp
```

确认里面能找到：

```text
llama-server.exe
```

如果看不到 `.exe`，可能是 Windows 隐藏了文件扩展名。只要能看到名为 `llama-server`、类型为“应用程序”的文件，也可以。

---

## 第四步：在正确的位置打开终端

下面的方法不需要手动输入文件夹地址。

1. 打开文件资源管理器。
2. 进入：

```text
D:\llama.cpp
```

3. 在文件夹的空白处点击鼠标右键。
4. 点击“在终端中打开”。

Windows 11 一般会直接看到“在终端中打开”。

Windows 10 如果没有这个选项，可以这样操作：

1. 打开 `D:\llama.cpp`。
2. 点击窗口上方显示文件夹位置的地址栏。
3. 输入：

```text
cmd
```

4. 按回车。

这时会出现一个黑色窗口，并且最后一行左边应该显示：

```text
D:\llama.cpp>
```

看到这个位置，说明终端打开正确。

---

## 第五步：复制一整行命令并启动

把下面这一整行命令完整复制：

```cmd
D:\llama.cpp\llama-server.exe -m D:\Unlimited-OCR\baidu.Unlimited-OCR.Q8_0.gguf -mm D:\Unlimited-OCR\mmproj-baidu.Unlimited-OCR.f16.gguf -ngl all -c 16384 --temp 0 -n 4096 -b 4096 -ub 1024 --mtmd-batch-max-tokens 2048
```

然后：

1. 回到刚刚打开的终端窗口。
2. 在窗口中右键点击粘贴命令。
3. 按回车。

不要把命令拆成多行，也不要自己增加或删除空格。

程序启动时，终端里会不断出现文字。这是正常现象。

第一次启动可能需要等待一会儿，因为程序需要读取体积很大的模型文件。

---

## 第六步：在浏览器中打开使用页面

当终端中的文字暂时停止滚动，并且没有立即出现红色错误时，打开浏览器。

在浏览器地址栏输入：

```text
http://127.0.0.1:8080
```

然后按回车。

如果页面能够打开，说明 Unlimited OCR 已经成功在本地运行。

接下来可以在网页中寻找上传图片的位置，选择需要识别的图片进行识别。

在使用过程中，不要关闭刚才的终端窗口。

关闭终端窗口，就等于关闭 Unlimited OCR 服务。

---

## 下次怎么启动

以后不需要重新下载文件。

每次使用时只做下面几步：

1. 打开 `D:\llama.cpp`。
2. 在空白处点击鼠标右键。
3. 点击“在终端中打开”。
4. 复制并运行下面这一整行命令：

```cmd
D:\llama.cpp\llama-server.exe -m D:\Unlimited-OCR\baidu.Unlimited-OCR.Q8_0.gguf -mm D:\Unlimited-OCR\mmproj-baidu.Unlimited-OCR.f16.gguf -ngl all -c 16384 --temp 0 -n 4096 -b 4096 -ub 1024 --mtmd-batch-max-tokens 2048
```

5. 浏览器打开：

```text
http://127.0.0.1:8080
```

---

## 常见问题

### 1. 提示找不到文件

如果终端中出现类似“找不到文件”或“failed to open model”的内容，通常是文件没有放到规定位置。

请分别检查：

```text
D:\Unlimited-OCR\baidu.Unlimited-OCR.Q8_0.gguf
```

```text
D:\Unlimited-OCR\mmproj-baidu.Unlimited-OCR.f16.gguf
```

```text
D:\llama.cpp\llama-server.exe
```

最简单的检查方法是：把上面的地址复制到文件资源管理器的地址栏，然后按回车。

### 2. 双击命令后窗口一闪就没了

不要直接双击 `llama-server.exe`。

请按照本文第四步，在 `D:\llama.cpp` 文件夹里打开终端，然后粘贴完整命令。

这样即使出现错误，窗口也不会立刻消失，可以看到具体提示。

### 3. 出现显存不足、内存不足或程序直接退出

先尝试使用下面这一行较省资源的命令：

```cmd
D:\llama.cpp\llama-server.exe -m D:\Unlimited-OCR\baidu.Unlimited-OCR.Q8_0.gguf -mm D:\Unlimited-OCR\mmproj-baidu.Unlimited-OCR.f16.gguf -ngl auto -c 8192 --temp 0 -n 2048 -b 1024 -ub 256 --mtmd-batch-max-tokens 512
```

复制整行、粘贴到终端，然后按回车。

如果还是无法启动，可能是电脑内存或显存不足以运行这个模型。此时需要换用更小的模型文件，或者在配置更高的电脑上运行。

### 4. 浏览器打不开 `127.0.0.1:8080`

请检查：

- 终端窗口是否仍然开着；
- 终端里是否出现了明显的错误；
- 是否在模型还没加载完成时就打开了网页；
- 电脑上的 8080 端口是否被其他程序占用。

可以先关闭终端，再重新按照第五步启动。

### 5. Windows 提示程序有风险

请确认 `llama.cpp` 是从下面这个官方 GitHub 页面下载的：

<https://github.com/ggml-org/llama.cpp/releases>

不要从不明网盘、论坛附件或第三方软件下载站下载。

如果确认来源正确，可以在 Windows 安全提示中点击“更多信息”，再根据自己的判断选择是否运行。

---

## 本文使用的下载地址

Unlimited OCR 模型：

<https://www.modelscope.cn/models/DevQuasar/baidu.Unlimited-OCR-GGUF/files>

llama.cpp 官方下载页面：

<https://github.com/ggml-org/llama.cpp/releases>
