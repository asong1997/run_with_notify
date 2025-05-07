import argparse
import subprocess
import time
import sys
import shlex
from notifier.email_sender import send_email
from notifier.config import default_from_email,default_password,default_to_email


import os
import pty

def run_command(command, stream=True):
    if stream:
        # 使用伪终端强制子进程行缓冲
        master_fd, slave_fd = pty.openpty()
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=slave_fd,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            executable="/bin/bash",
            env={"PYTHONUNBUFFERED": "1", **os.environ}  # 注入环境变量
        )
        os.close(slave_fd)  # 关闭子进程端，避免资源泄漏

        output_lines = []
        try:
            while True:
                try:
                    data = os.read(master_fd, 1024)
                except OSError:
                    break  # 当子进程关闭后读取会抛出异常
                if not data:
                    break
                decoded = data.decode(errors='replace')
                print(decoded, end='', flush=True)
                output_lines.append(decoded)
        finally:
            os.close(master_fd)  # 确保关闭主端
            process.wait()

        return process.returncode, ''.join(output_lines)
    else:
        # 非流模式保持原逻辑
        result = subprocess.run(
            command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.returncode, result.stdout




def run_command_with_notify(command, task_name, stream, from_email, password, to_email,
                            max_retry=1, retry_interval=60):
    retry_count = 0
    success = False
    start_time = time.time()
    start_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))

    while retry_count < max_retry:
        print(f"\n🚀 开始执行任务：{task_name}（第 {retry_count + 1} 次尝试）")
        return_code, output = run_command(command, stream=stream)
        if return_code == 0:
            success = True
            break
        else:
            retry_count += 1
            print(f"⚠️ 第 {retry_count} 次失败，准备重试...")
            print(f"⏳ 等待 {retry_interval}s 后重试...\n")
            time.sleep(retry_interval)


    end_time = time.time()
    duration = end_time - start_time
    duration_str = time.strftime("%H:%M:%S", time.gmtime(duration))

    if success:
        subject = f"✅ 任务成功：{task_name}"
        body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <b>✅ {task_name}</b> 执行成功 🎉<br><br>
                🕒 开始时间: {start_str}<br>
                ⏱️ 耗时: <b>{duration_str}</b><br>
                📬 结果: <b style="color:green;">执行成功 ✅</b><br><br>
                📄 日志输出：<br>
                <pre style="background-color:#f6f8fa;border:1px solid #ddd;padding:10px;overflow-x:auto;">
    {output.strip()}
                </pre>
            </body>
            </html>
            """
    else:
        subject = f"❌ 任务失败：{task_name}"
        body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <b>❌ {task_name}</b> 执行失败 😞<br><br>
                🕒 开始时间: {start_str}<br>
                ⏱️ 耗时: <b>{duration_str}</b><br>
                🔁 尝试次数: <b>{max_retry}</b><br>
                📬 结果: <b style="color:red;">执行失败 ❌</b><br><br>
                📄 日志输出：<br>
                <pre style="background-color:#f6f8fa;border:1px solid #ddd;padding:10px;overflow-x:auto;">
    {output.strip()}
                </pre>
            </body>
            </html>
            """
    send_email(subject, body, from_email, password, to_email)

def main():
    parser = argparse.ArgumentParser(description="Run bash command with email notification")
    parser.add_argument("command", help="Shell command to execute (use quotes)")
    parser.add_argument("--task", default="Shell任务", help="任务名称")
    parser.add_argument("--max-fails", type=int, default=3, help="最多失败次数")
    parser.add_argument("--retry-interval", type=int, default=60, help="失败重试间隔秒数")
    parser.add_argument("--from-email", default=default_from_email, help="发件人邮箱")
    parser.add_argument("--password", default=default_password, help="发件人授权码")
    parser.add_argument("--to-email", default=default_to_email, help="接收通知的邮箱")
    parser.add_argument("--stream", action="store_true", help="是否将任务执行过程的 stdout/stderr 实时打印到终端")

    args = parser.parse_args()

    run_command_with_notify(
        args.command,
        args.task,
        args.stream,
        args.from_email,
        args.password,
        args.to_email,
        args.max_fails,
        args.retry_interval
    )

if __name__ == "__main__":
    main()