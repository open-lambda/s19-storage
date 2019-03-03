from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
from io import BytesIO
import requests
import base64

SERVER_IP = "107.22.151.56"
PORT = "8080"
TEMPLATE = "http://{ip}:{port}/runLambda/{command}"

class App(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.response = ''
        self.img = None

        master.title("Storage Team Edge Computing Demo")

        self.aws_access_key_id = Entry(master)

        self.aws_access_key_id_text = Label(master, text="AWS access key id:")

        self.aws_secret_access_key = Entry(master)
        self.aws_secret_access_key_text = Label(master, text="AWS secret access key:")

        self.file_name = Entry(master)
        self.file_name_text = Label(master, text="picture file name:")

        self.command = Entry(master)
        self.command_text = Label(master, text="command:")

        self.request = Button(text='request', command = self.send_requests)

        self.response_label = ScrolledText(master)
        self.response_header_label = Label(master, text="OpenLambda response (first 200 characters):")

        self.panel = Label(master)

        self.file_name.insert(0, '1.jpg')
        self.command.insert(0,'fetch')

        self.aws_access_key_id_text.grid(row = 0, column = 0)
        self.aws_access_key_id.grid(row = 0, column = 1)
        self.aws_secret_access_key_text.grid(row = 1, column = 0)
        self.aws_secret_access_key.grid(row = 1, column = 1)
        self.file_name_text.grid(row = 2, column = 0)
        self.file_name.grid(row = 2, column = 1)
        self.command_text.grid(row = 3, column = 0)
        self.command.grid(row = 3, column = 1)

        self.request.grid(row = 4, padx = 5, pady = 5)
        self.response_header_label.grid(row = 5)
        self.response_label.grid(row = 6, columnspan = 2)

        self.panel.grid(row = 0, rowspan = 6, column = 2)

        # and here we get a callback when the user hits return.
        # we will have the program print out the value of the
        # application variable when the user hits return

    def print_contents(self):
        print("hi")

    def send_requests(self):
        tokens = self.command.get().split(' ')
        url = TEMPLATE.format(ip=SERVER_IP, port=PORT, command=tokens[0])
        data =  {'aws_access_key_id': self.aws_access_key_id.get(),
                 'aws_secret_access_key': self.aws_secret_access_key.get(),
                 'file_name': self.file_name.get()}
        if tokens[0] == 'resize':
            data['width'] = int(tokens[1])
            data['height'] = int(tokens[2])
        print(url, data)
        r = requests.post(url, json = data)
        result = r.text
        if (len(result) >= 200):
            result = result[:200] + '...'
        self.response_label.insert(0.0, result)
        print(r.text)
        print(len(r.text))

        self.img = ImageTk.PhotoImage(Image.open(BytesIO(base64.b64decode(r.text))))
        self.panel.configure(image=self.img)
        self.panel.image = self.img



root = Tk()
app = App(master=root)
app.mainloop()
