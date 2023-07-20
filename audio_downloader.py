import subprocess
import re
import os
def download_m3u8(link,dest,meta_data):
    subprocess.run(["ffmpeg", "-http_persistent", "false", "-i", link, "-c", "copy", "-b:a", "320k", dest])

    args = ["ate", dest, "artist:"+meta_data["artist"],"title:"+meta_data["title"]]
    if meta_data["album"] != "":
        args.append("album:"+meta_data["album"])
    subprocess.run(args)

def __create_folder_to_download():
    folder = input("enter path, where files will be downloaded:")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder

def __input_wrapper(s):
    try:
        result = input(s)
    except KeyboardInterrupt:
        return ""
    return result
def download(items):
    '''optional ability that is invoked by find function'''
    choice = __input_wrapper("Do you want to download something?(y/n)")

    if "n" == choice:
        return 1
    elif "y" == choice:
        urls = list()
        
        args = __input_wrapper("specify what you need:")
        if args == "all":
            #get all urls
            urls = items[:]
                
        elif "-" in args:
            #get urls in range
            pattern = re.compile("\d*-\d*")
            if pattern.match(args):

                left, right = args.split("-")
                left = int(left)
                right = int(right)
                
                if left in range(len(items)) and right in range(len(items)):
                    for i in range(left,right+1):
                        urls.append(items[i])
                else:
                    return None
            else:
                print("incorrect arguments!")
                return None
            
        elif "," in args:
            args = args.split(",")
            for arg in args:
                if arg.isnumeric() and int(arg) in range(len(items)):
                    urls.append(items[int(arg)])
                else:
                    return None
                
        else:
            if args.isnumeric():
                urls.append(items[int(args)])
            else:
                return None

    _dir = __create_folder_to_download()
    for i in urls:
        name = i[1]+" "+i[0]
        meta_data = {}
        meta_data["artist"] = i[1]
        meta_data["title"] = i[0]
        meta_data["album"] = "" if i[3] == "none" else i[3]
        download_m3u8(i[2],_dir+"/"+name+".mp3",meta_data)
    return 1
