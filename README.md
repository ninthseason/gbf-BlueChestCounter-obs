OBS插件

将https://github.com/sinyang92/gbf-BlueChestCounter的数据发送给OBS，绑定文字源显示在屏幕上。

使用方法：
在OBS中添加`gbf.py`脚本，点击`启动监听`按钮启动服务端用于监听发送来的数据。

chrome中打开`chrome-extension://<extension-id>/src/browser_action/browser_action.html`页面，F12打开控制台，执行转发代码。该代码每秒向OBS脚本的服务端发送数据。

OBS脚本将在接收到数据后将数据显示到绑定的文字源上。