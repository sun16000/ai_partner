#读文件
# 1.打开文件
try:
    f = open("resources/望庐山瀑布.txt", "r", encoding="utf-8")

    # 2.读取文件内容
    # content = f.read()
    # print(content)
    # 2.逐行读取
    content_list = f.readlines()
    for line in content_list:
        print(line.strip())

    print(1/0)

except Exception as e:
    print(f"读取文件过程中发生了异常：{e}")
finally:
    # 3.关闭文件
    f.close()
    print("文件已关闭！")


# 写文件
# with语句(上下文管理器)的核心作用就是确保资源总是被正确获取和释放（即使发生异常，也会被正确释放）
with open("resources/filewriter.txt", "w", encoding="utf-8") as file1:
    file1 = open("resources/filewriter.txt", "w", encoding="utf-8")
    file1.write("你好！\n")
    file1.write("你是谁？\n")
    file1.write("你从哪里来？\n")
    print(1/0)  #有异常，此语句后面的不会再执行，会关闭文件
    file1.write("要到哪里去？\n")
    # 文件已自动关闭，无需手动调用 close()
    # file.close()

print("文件写入成功！")