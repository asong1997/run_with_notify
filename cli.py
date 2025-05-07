import argparse
import subprocess
import time
import sys
from email_sender import send_email
from config import default_from_email,default_password,default_to_email

def run_command_with_notify(command, task_name, from_email, password, to_email,
                            max_failures=1, retry_interval=60):
    start_time = time.time()
    start_str = time.strftime('%Y-%m-%d %H:%M:%S')

    for attempt in range(1, max_failures + 1):
        print(f"🚀 执行任务 [{task_name}]：第 {attempt}/{max_failures} 次尝试")
        try:
            result = subprocess.run(command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # 成功
            end_time = time.time()
            duration = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
            subject = f"✅ 任务完成: {task_name}"
            body = f"""
            <b>{task_name}</b> 成功完成 🎉<br><br>
            🕒 开始时间: {start_str}<br>
            ✅ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            ⏱️ 耗时: <b>{duration}</b><br>
            🔁 尝试次数: {attempt}<br><br>
            <pre>{result.stdout}</pre>
            """
            send_email(subject, body, from_email, password, to_email)
            return

        except subprocess.CalledProcessError as e:
            print(f"⚠️ 失败：{e.stderr}")
            if attempt < max_failures:
                print(f"⏳ 等待 {retry_interval}s 后重试...\n")
                time.sleep(retry_interval)
            else:
                end_time = time.time()
                duration = time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))
                subject = f"❌ 任务最终失败: {task_name}"
                body = f"""
                <b>{task_name}</b> 最终失败！<br><br>
                🕒 开始时间: {start_str}<br>
                ❌ 最后失败时间: {time.strftime('%Y-%m-%d %H:%M:%S')}<br>
                ⏱️ 耗时: <b>{duration}</b><br>
                🔁 尝试次数: {attempt}<br><br>
                <b>命令:</b> <code>{command}</code><br><br>
                <b>错误输出:</b><br><pre>{e.stderr}</pre>
                """
                send_email(subject, body, from_email, password, to_email)
                sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run bash command with email notification")
    parser.add_argument("command", help="Shell command to execute (use quotes)")
    parser.add_argument("--task", default="Shell任务", help="任务名称")
    parser.add_argument("--max-fails", type=int, default=3, help="最多失败次数")
    parser.add_argument("--retry-interval", type=int, default=60, help="失败重试间隔秒数")
    parser.add_argument("--from-email", default=default_from_email, help="发件人邮箱")
    parser.add_argument("--password", default=default_password, help="发件人授权码")
    parser.add_argument("--to-email", default=default_to_email, help="接收通知的邮箱")
    args = parser.parse_args()

    run_command_with_notify(
        args.command,
        args.task,
        args.from_email,
        args.password,
        args.to_email,
        args.max_fails,
        args.retry_interval
    )

if __name__ == "__main__":
    main()