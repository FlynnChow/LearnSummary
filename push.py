# encoding: utf-8
import sys
import os

def getTypeName(fileName):
    if fileName == "kotlin":
        return "Kotlin总结"
    elif fileName == "android":
        return "Android总结"
    elif fileName == "java":
        return "Java总结"
    elif fileName == "android":
        return "Android总结"
    elif fileName == "flutter":
        return "Flutter总结"
    elif fileName == "ffmpeg":
        return "FFmpeg总结"
    elif fileName == "openGL":
        return "OpenGL总结"
    elif fileName == "network":
        return "计算机网络总结"
    elif fileName == "os":
        return "操作系统总结"
    elif fileName == "database":
        return "数据库总结"
    elif fileName == "code_design":
        return "设计模式总结"
    elif fileName == "other":
        return "其他总结"
    else:
        return ""

def initDir(path,name):
    readme = path + '/' + "README.md"
    os.system('echo "## ' + name + '\n" > ' + readme)
    file_list = os.listdir(path+"/")
    file_list.sort()
    count = 0
    for index in range(0,len(file_list)):
        if (os.path.basename(file_list[index]) != "README.md"):
            fileName,type = os.path.splitext(os.path.basename(file_list[index]))
            if type == '.md':
                count += 1
                inputName = '[' + fileName + ']' + '(' + path + '/' + file_list[index] + ')'
                os.system('echo "* ' + inputName + '\n" >> ' + readme)
    if count > 0:print("已更新" + name + " Count[" + str(count) +"]")

msg = ''
if len(sys.argv) >= 2:
    msg = sys.argv[1]
else:
    msg = "update content"

file_list = os.listdir("./")
for index in range(0,len(file_list)):
    if(os.path.isdir(file_list[index])):
        name = getTypeName(os.path.basename(file_list[index]))
        if name == '':continue
        initDir(file_list[index],name)

os.system('git add .')
os.system('git commit -m "' + msg + '"')
os.system('git push origin master')
print("成功提交到GitHub")
