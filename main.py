import os
import tkinter
import chromedriver_autoinstaller
import time

from tkinter import messagebox
from selenium import webdriver


def get_student_list(file_name: str) -> list:
    with open('./class_list/' + file_name, 'r', encoding='utf8') as student_file:
        return list(map(lambda x: x.strip(), student_file.readlines()))


def get_class_list() -> list:
    return os.listdir('class_list')


def is_current_site_starts(url: str):
    cur_url = driver.current_url
    if len(url) > len(cur_url):
        return False
    return cur_url[:len(url)] == url


def run_driver() -> None:
    global driver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(time_to_wait=5)
    driver.get('https://classroom.google.com/u/0/h')


def get_students_by_js_classname(classname: str) -> list:
    return [i.text.strip() for i in driver.find_elements_by_class_name(classname)]


def generate_class_file(name: str):
    if name == '':
        messagebox.showwarning('경고', '이름을 입력해주세요')
        return
    student_list = get_students_by_js_classname('y4ihN')
    if len(student_list) == 0:
        messagebox.showwarning('경고', '구글 클래스룸 -> 사용자 칸으로 들어간 후\n다시 클릭해주세요')
    else:
        with open('./class_list/' + name + '.txt', 'w', encoding='utf8') as class_file:
            for i in student_list:
                print(i, file=class_file)


def update_list_listbox(lb, value: list):
    lb.delete(0, 'end')
    lb.insert('end', *value)


def check_not_joined_and_mistake_joined(class_name) -> list:
    student_list = get_student_list(class_name)
    joined_student_list = get_students_by_js_classname('ZjFb7c')
    if len(joined_student_list) == 0:
        messagebox.showwarning('경고', '우측하단 모두에게 표시 버튼을 클릭 후 다시 눌러주세요')
        return [[], []]
    else:
        not_joined_student_list = [i for i in student_list if i not in joined_student_list]
        mistake_joined_student_list = [i for i in joined_student_list if i not in student_list]
        return [not_joined_student_list, mistake_joined_student_list]


def attendance():
    if class_lb.curselection():
        selected_class = class_lb.get(class_lb.curselection())
        not_joined_student_list, mistake_joined_student_list = check_not_joined_and_mistake_joined(selected_class)
        update_list_listbox(not_joined_student_lb, not_joined_student_list)
        update_list_listbox(mistake_joined_student_lb, mistake_joined_student_list)
    else:
        messagebox.showwarning('경고', '아직 어떠한 항목도 선택하지 않았습니다')


def delete():
    if class_lb.curselection():
        selected_class = class_lb.get(class_lb.curselection())
        os.remove('./class_list/' + selected_class)
        update_list_listbox(class_lb, get_class_list())
    else:
        messagebox.showwarning('경고', '아직 어떠한 항목도 선택하지 않았습니다')


def add():
    sub_window = tkinter.Toplevel(window)
    sub_window.geometry("200x160+860+460")
    sub_window.resizable(False, False)
    tkinter.Label(sub_window, text='등록될 파일의 이름을 입력하세요').pack(side='top')
    class_name_entry = tkinter.Entry(sub_window)
    class_name_entry.pack(side='top', fill='x')
    confirm_add_button = tkinter.Button(sub_window, text='추가하기', width=7, height=2,
                                        command=lambda: generate_class_file(class_name_entry.get().strip())
                                        or class_name_entry.delete(0, 'end')
                                        or update_list_listbox(class_lb, get_class_list()))
    confirm_add_button.pack(side='top')


def copy_not_joined_student() -> None:
    window.clipboard_clear()
    window.clipboard_append('\n'.join(not_joined_student_lb.get(0, 'end')))
    messagebox.showinfo('알림', '미참여자 목록이 복사되었습니다')


def get_chat_list() -> list:
    get_chats = driver.find_elements_by_class_name('GDhqjd')
    chat_and_times = []
    for i in get_chats:
        temp = i.text.split()[0]
        name = temp[:len(temp)-2]
        time = int(i.get_attribute('data-timestamp'))/1000
        chat_and_times.append((name, time))
    return chat_and_times


def restart_chrome():
    try:
        driver.close()
    except:
        pass
    run_driver()


def get_not_chatted(standard_time):
    if class_lb.curselection():
        selected_class = class_lb.get(class_lb.curselection())
        joined_student = get_student_list(selected_class)
        removed_student = set()
        for name, time in get_chat_list():
            if time > standard_time and name not in removed_student:
                removed_student.add(name)
                try:
                    joined_student.remove(name)
                except ValueError:
                    pass
        return joined_student
    else:
        messagebox.showwarning('경고', '아직 어떠한 항목도 선택하지 않았습니다')


def set_time():
    global standard_time
    standard_time = time.time()


def chat_screen():
    global standard_time
    standard_time = time.time()

    sub_window = tkinter.Toplevel(window)
    sub_window.geometry("340x400+100+100")
    sub_window.resizable(False, False)

    left_chat_frame = tkinter.Frame(sub_window, relief="solid", bd=2)
    right_chat_frame = tkinter.Frame(sub_window, relief="solid", bd=2)

    every_chat_scroll = tkinter.Scrollbar(left_chat_frame)
    after_chat_scroll = tkinter.Scrollbar(right_chat_frame)

    every_chat_lb = tkinter.Listbox(left_chat_frame, selectmode='browse', yscrollcommand=every_chat_scroll.set)
    after_chat_lb = tkinter.Listbox(right_chat_frame, selectmode='browse', yscrollcommand=after_chat_scroll.set)

    every_chat_scroll.config(command=every_chat_lb.yview)
    after_chat_scroll.config(command=every_chat_lb.yview)

    tkinter.Label(sub_window, text='채팅을 치지 않은 학생 목록').pack(side='top')
    tkinter.Label(left_chat_frame, text='이번 수업기준').pack(side='top', fill='x')
    tkinter.Label(right_chat_frame, text='창이 켜진이후 기준').pack(side='top', fill='x')

    tkinter.Button(left_chat_frame, text='새로고침',
                   command=lambda: update_list_listbox(every_chat_lb, get_not_chatted(0))
                   or update_list_listbox(after_chat_lb, get_not_chatted(standard_time))).pack(side='bottom', fill='x')
    tkinter.Button(right_chat_frame, text='초기화',
                   command=lambda: set_time() or update_list_listbox(every_chat_lb, get_not_chatted(0))
                   or update_list_listbox(after_chat_lb, get_not_chatted(standard_time))).pack(side='bottom', fill='x')

    every_chat_lb.pack(side='left', fill='both')
    after_chat_lb.pack(side='left', fill='both')

    every_chat_scroll.pack(side='right', fill='y')
    after_chat_scroll.pack(side='right', fill='y')

    left_chat_frame.pack(side='left', fill='both', expand=True)
    right_chat_frame.pack(side='right', fill='both', expand=True)


if __name__ == '__main__':
    if not os.path.isdir('./class_list'):
        os.mkdir('./class_list')
    chromedriver_autoinstaller.install(True)
    standard_time = 0
    options = webdriver.ChromeOptions()
    options.add_argument('start-maximized')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    run_driver()

    window = tkinter.Tk()
    window.title('Attendance')
    window.geometry("558x440+100+100")
    window.resizable(False, False)

    left_frame = tkinter.Frame(window, relief="solid", bd=2)
    mid_left_frame = tkinter.Frame(window, relief="solid", bd=2)
    mid_right_frame = tkinter.Frame(window, relief="solid", bd=2)
    right_frame = tkinter.Frame(window, relief="solid", bd=2)

    class_scroll = tkinter.Scrollbar(left_frame)
    not_joined_student_scroll = tkinter.Scrollbar(mid_left_frame)
    mistake_joined_student_scroll = tkinter.Scrollbar(mid_right_frame)

    class_lb = tkinter.Listbox(left_frame, selectmode='browse', height=24, yscrollcommand=class_scroll.set)
    not_joined_student_lb = tkinter.Listbox(mid_left_frame, selectmode='browse', height=24,
                                            yscrollcommand=not_joined_student_scroll.set)
    mistake_joined_student_lb = tkinter.Listbox(mid_right_frame, selectmode='browse', height=24,
                                                yscrollcommand=mistake_joined_student_scroll.set)
    update_list_listbox(class_lb, get_class_list())

    attendance_button = tkinter.Button(right_frame, text='출석확인', height=3, command=attendance)
    add_button = tkinter.Button(right_frame, text='추가하기', height=3, command=add)
    delete_button = tkinter.Button(right_frame, text='삭제하기', height=3, command=delete)
    copy_button = tkinter.Button(right_frame, text='미참여자\n복사하기', height=3, command=copy_not_joined_student)
    check_chat_button = tkinter.Button(right_frame, text='채팅감지', height=3, command=chat_screen)
    restart_chrome_button = tkinter.Button(right_frame, text='인터넷창\n재시작', height=3, command=restart_chrome)

    tkinter.Label(left_frame, text='반 선택하기').pack(side='top')
    tkinter.Label(mid_left_frame, text='접속하지 않은 학생').pack(side='top')
    tkinter.Label(mid_right_frame, text='잘못 접속한 학생').pack(side='top')

    attendance_button.pack(side='top', fill='x')
    add_button.pack(side='top', fill='x')
    delete_button.pack(side='top', fill='x')
    copy_button.pack(side='top', fill='x')
    check_chat_button.pack(side='top', fill='x')
    restart_chrome_button.pack(side='top', fill='x')

    class_scroll.pack(side='right', fill='y')
    not_joined_student_scroll.pack(side='right', fill='y')
    mistake_joined_student_scroll.pack(side='right', fill='y')

    class_lb.pack(side='left', fill='both')
    not_joined_student_lb.pack(side='left', fill='both')
    mistake_joined_student_lb.pack(side='left', fill='both')

    class_scroll.config(command=class_lb.yview)
    not_joined_student_scroll.config(command=not_joined_student_lb.yview)
    mistake_joined_student_scroll.config(command=mistake_joined_student_lb.yview)

    left_frame.pack(side='left', fill='y')
    mid_left_frame.pack(side='left', fill='y')
    mid_right_frame.pack(side='left', fill='y')
    right_frame.pack(side='left', fill='y')

    window.mainloop()
    try:
        driver.close()
    except BaseException:
        pass
