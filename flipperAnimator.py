import os
import wx
from PIL import Image

def make_gif_2color(input_path, folder_name, threshold, skip_frames):
    image = Image.open(input_path)
    frames = []

    try:
        while True:
            grayscale_frame = image.convert("L")
            binary_frame = grayscale_frame.point(lambda x: 0 if x < threshold else 255, "1")
            resized_frame = binary_frame.resize((128, 64))
            frames.append(resized_frame)
            image.seek(image.tell() + skip_frames)  # 使用输入的跳过帧数
    except EOFError:
        pass

    if folder_name:
        frames_dir = folder_name
        os.makedirs(frames_dir, exist_ok=True)

        frame_order = []
        for i, frame in enumerate(frames):
            frame_filename = os.path.join(frames_dir, f"frame_{i}.png")
            frame.save(frame_filename, format="PNG")
            frame_order.append(str(i))

        manifest_path = os.path.join(frames_dir, "meta.txt")
        with open(manifest_path, "w") as manifest_file:
            manifest_file.write("Filetype: Flipper Animation\n")
            manifest_file.write("Version: 1\n\n")
            manifest_file.write("Width: 128\n")
            manifest_file.write("Height: 64\n")
            manifest_file.write("Passive frames: {}\n".format(len(frames)))
            manifest_file.write("Active frames: 0\n")
            manifest_file.write("Frames order: {}\n".format(" ".join(frame_order)))
            manifest_file.write("Active cycles: 0\n")
            manifest_file.write("Frame rate: 6\n")
            manifest_file.write("Duration: " + str(28800) + "\n")
            manifest_file.write("Active cooldown: 0\n\n")
            manifest_file.write("Bubble slots: 0\n")

    return frames  # 返回帧用于预览

class PreviewFrame(wx.Frame):
    def __init__(self, frames, *args, **kw):
        super(PreviewFrame, self).__init__(*args, **kw)

        self.frames = frames
        self.index = 0

        self.panel = wx.Panel(self)
        self.image_ctrl = wx.StaticBitmap(self.panel)
        self.update_image()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.image_ctrl, 0, wx.CENTER | wx.ALL, 10)

        self.panel.SetSizer(sizer)

        self.SetTitle("预览")
        self.SetSize((400, 400))  # 调整窗口大小
        self.Centre()

    def update_image(self):
        if self.frames:
            img = self.frames[self.index]
            wx_image = wx.Image(img.size[0], img.size[1])
            wx_image.SetData(img.convert("RGB").tobytes())

            # 放大图像，例如放大2倍
            scaled_image = wx_image.Scale(img.size[0] * 2, img.size[1] * 2)  # 根据需要调整放大倍数
            self.image_ctrl.SetBitmap(wx.Bitmap(scaled_image))

            self.index = (self.index + 1) % len(self.frames)
            wx.CallLater(100, self.update_image)  # 每100ms更新一次

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        panel = wx.Panel(self)

        # 使用BoxSizer进行左右布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 创建一个GridSizer用于输入项
        input_sizer = wx.GridSizer(rows=4, cols=2, hgap=10, vgap=10)

        # 标签和控件
        label1 = wx.StaticText(panel, label="GIF文件选择：")
        label2 = wx.StaticText(panel, label="输出文件夹选择：")
        label3 = wx.StaticText(panel, label="自定义阈值：")
        label4 = wx.StaticText(panel, label="帧/秒：")

        self.file_picker = wx.FilePickerCtrl(panel, message="选择GIF文件")
        self.folder_picker = wx.DirPickerCtrl(panel, message="选择输出文件夹")
        self.threshold_input = wx.TextCtrl(panel, value="200")  # 阈值输入框，默认值为200
        self.skip_frames_input = wx.TextCtrl(panel, value="1")  # 跳过帧数输入框，默认值为1

        # 将标签和控件添加到input_sizer
        input_sizer.Add(label1, 0, wx.ALIGN_CENTER)
        input_sizer.Add(self.file_picker, 1, wx.EXPAND)
        input_sizer.Add(label2, 0, wx.ALIGN_CENTER)
        input_sizer.Add(self.folder_picker, 1, wx.EXPAND)
        input_sizer.Add(label3, 0, wx.ALIGN_CENTER)
        input_sizer.Add(self.threshold_input, 1, wx.EXPAND)
        input_sizer.Add(label4, 0, wx.ALIGN_CENTER)
        input_sizer.Add(self.skip_frames_input, 1, wx.EXPAND)

        # 将输入项添加到主sizer中
        main_sizer.Add(input_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # 按钮水平布局
        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        generate_button = wx.Button(panel, label="生成2色GIF")
        generate_button.Bind(wx.EVT_BUTTON, self.on_generate)

        preview_button = wx.Button(panel, label="预览")
        preview_button.Bind(wx.EVT_BUTTON, self.on_preview)

        button_hbox.Add(generate_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        button_hbox.Add(preview_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        # 将按钮添加到主sizer
        main_sizer.Add(button_hbox, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(main_sizer)

        self.SetTitle("GIF转换工具")
        self.SetSize((400, 300))
        self.Centre()

    def on_generate(self, event):
        input_file = self.file_picker.GetPath()
        folder_name = self.folder_picker.GetPath()
        try:
            threshold = int(self.threshold_input.GetValue())
            skip_frames = int(self.skip_frames_input.GetValue())  # 获取跳过帧数
        except ValueError:
            wx.MessageBox("请输入有效的阈值（整数）和跳过帧数！", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not input_file or not folder_name:
            wx.MessageBox("请选择文件和输出文件夹！", "Error", wx.OK | wx.ICON_ERROR)
        else:
            make_gif_2color(input_file, folder_name, threshold, skip_frames)
            wx.MessageBox("生成成功！", "成功", wx.OK | wx.ICON_INFORMATION)

    def on_preview(self, event):
        input_file = self.file_picker.GetPath()
        try:
            threshold = int(self.threshold_input.GetValue())
            skip_frames = int(self.skip_frames_input.GetValue())  # 获取跳过帧数
        except ValueError:
            wx.MessageBox("请输入有效的阈值（整数）和跳过帧数！", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not input_file:
            wx.MessageBox("请选择GIF文件！", "Error", wx.OK | wx.ICON_ERROR)
            return

        # 使用临时文件夹存储帧
        temp_folder = "temp_frames"
        frames = make_gif_2color(input_file, temp_folder, threshold, skip_frames)  # 生成帧用于预览
        preview_frame = PreviewFrame(frames, None)
        preview_frame.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
