安装步骤：
1、解压tools.zip文件任意路径下（最好不要是C盘）；
2、jetBrains系列IDE导入解压文件夹中的/idea/settings.jar配置；
3、双击运行tools目录下安装脚本setup.bat；
4、修改tools目录下setting.json配置文件，将userName改成自己的RTX名称，password可以置空；
5、重启jetBrains IDE

安装的要求：
python 2.7.3
jdk
并配置以上sdk的path环境变量

更新内容：
1、tools解压文件可以放在任意目录；
2、新增legos工具：
	addModelByPath:新增业务模块，需要在弹窗中输入项目id
	saveModelByPath:保存现有模块