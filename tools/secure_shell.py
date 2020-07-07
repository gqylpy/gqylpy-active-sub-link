import re
import os
import sys
import uuid
import paramiko


class SecureShell(object):
    _CLIENT = paramiko.SSHClient()

    _CONNECT_SEPARATED: str = ':'
    _AUTH_SEPARATED: str = '@'

    _CD: str = 'cd'
    _PWD: str = 'pwd'

    _PROMPT: str = '>>> '
    _HOSTNAME_LENGTH: int = 10

    _GET_HOSTNAME_CMD: str = 'echo $HOSTNAME'
    _GET_HOME_CMD: str = 'echo $HOME'

    _EXIT_INTERACTION: tuple = ('exit', 'quit', 'e', 'q')

    _ADMIN_NAME: str = 'root'
    _MARK: tuple = ('#', '$')
    _HOME_PATH_MARK: str = '~'
    _ROOT_PATH_MARK: str = '/'
    _NOW_PATH_MARK: str = ''
    _NOW_PATH_CMD: str = ''

    _UP_FILE_DEFAULT_PATH: str = '/root/'
    _UP_OR_DOWN_FILE_DEFAULT_SUFFIX: str = '.txt'
    _UP_SUCCESS_CLUES: str = 'Uploaded successfully -> %(filepath)s'
    _DOWN_SUCCESS_CLUES: str = 'Download successful -> %(filepath)s'
    _UP_FAILED_CLUES: str = 'Uploaded failed'
    _DOWN_FAILED_CLUES: str = 'Download failed'

    def __init__(self, connect: str, auth: str, timeout: int = 10):
        """
        :param connect: host:port
        :param auth: user@pwd
        """
        self.connect: tuple = connect.split(self._CONNECT_SEPARATED)
        self.auth: tuple = re.match(rf'(?P<u>.+?){self._AUTH_SEPARATED}(?P<p>.+)', auth).group('u', 'p')
        self.timeout: int = timeout
        self._connection()

    def _connection(self) -> None:
        self._CLIENT.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._CLIENT.connect(*self.connect, *self.auth, timeout=self.timeout)

    def _parse_result(self, result: 'stdout or stderr') -> str:
        return result.read().decode()

    def _print(self, data: str = '\n', color: int = 37, font: int = 0) -> None:
        print(f'\033[{font};{color};0m{data}\033[0m')

    def _set_prompt(self) -> str:
        try:
            hostname: str = self.cmd(self._GET_HOSTNAME_CMD)[1][:self._HOSTNAME_LENGTH + 1].strip()
            home: str = re.match(r'.*/(.+)', self.cmd(self._GET_HOME_CMD)[1].strip()).group(1)
            path_mark: str = self._HOME_PATH_MARK if self._NOW_PATH_MARK == home else \
                self._NOW_PATH_MARK if self._NOW_PATH_MARK else self._HOME_PATH_MARK
            mark: str = self._MARK[0] if self.auth[0] == self._ADMIN_NAME else self._MARK[1]
            return f'[{self.auth[0]}@{hostname} {path_mark}]{mark} ' if hostname else self._PROMPT
        except Exception:
            return self._PROMPT

    def _receive_cmd(self, flags: str) -> str or False:
        while True:
            cmd: str = input(flags or self._set_prompt()).strip()
            if cmd:
                break
        if cmd in self._EXIT_INTERACTION:
            return False
        if flags:
            return cmd
        now_path_cmd: str = self._NOW_PATH_CMD and self._NOW_PATH_CMD + ';'
        return f"{now_path_cmd}{re.sub(r';$', '', cmd)}&&{self._PWD}"

    def _ext_path_info(self, result: str, flags: str) -> str:
        if flags:
            return result
        pattern = re.compile(r'\n?(.+)\n$')
        now_path: str = pattern.findall(result)[0]
        self._NOW_PATH_MARK: str = now_path.split('/')[-1] or self._ROOT_PATH_MARK
        self._NOW_PATH_CMD: str = f'{self._CD} {now_path}'
        return pattern.sub('', result)

    def cmd(self, cmd: str) -> tuple:
        """Execute the command
        如果你的程序需要在远程服务器中执行命令并取得结果，可使用此方法
        :param cmd: 命令
        :return: 命令执行结果
        """
        stdin, stdout, stderr = self._CLIENT.exec_command(cmd, self.timeout)
        result: str = self._parse_result(stdout)
        return bool(result), result or self._parse_result(stderr)

    def cmdp(self, cmd: str, print_color: int = 37, print_font: int = 0, *args, **kwargs) -> None:
        """Execute the command and print
        直接输出命令结果
        :param cmd: 命令
        :param print_color: 输出字符颜色
        :param print_font: 输出字符字体
        """
        stdin, stdout, stderr = self._CLIENT.exec_command(cmd, self.timeout)
        result: str = self._parse_result(stdout) or self._parse_result(stderr)
        self._print(result, print_color, print_font)

    def cmdp_while(self, flags: str = None, print_color: int = 37, print_font: int = 0, *args, **kwargs) -> None:
        """Interactive mode
        交互模式，类似于终端，使用例如 "tail -f file" 的指令会导致程序卡死
        :param flags: 交互提示符
        :param print_color: 打印字符颜色
        :param print_font: 打印字符字体
        """
        while True:
            try:
                cmd: str = self._receive_cmd(flags)
                if not cmd:
                    break
                stdin, stdout, stderr = self._CLIENT.exec_command(cmd, self.timeout)
                result: str = self._parse_result(stdout)
                result: str = self._ext_path_info(result, flags) if result else self._parse_result(stderr)
                self._print(result or ' ', print_color, print_font)
            except KeyboardInterrupt:
                break

    def upload_file(self, local_path: str, remote_path: str = None, flags: bool = False, *args, **kwargs) -> True or None:
        """Upload file
        上传文件
        :param local_path: 本地路径
        :param remote_path: 远程路径
        :param flags: 是否在输出相关信息
        """
        remote_path: str = remote_path or \
                           f'{self._UP_FILE_DEFAULT_PATH}{str(uuid.uuid4())}{self._UP_OR_DOWN_FILE_DEFAULT_SUFFIX}'
        if self._CLIENT.open_sftp().put(local_path, remote_path):
            flags and self._print(self._UP_SUCCESS_CLUES % {'filepath': remote_path}, 32)
            return True
        self._print(self._UP_FAILED_CLUES, 31)

    def download_file(self, remote_path: str, local_path: str = None, flags: bool = False, *args, **kwargs) -> True or None:
        """Download file
        下载文件
        :param remote_path: 远程路径
        :param local_path: 本地路径
        :param flags: 是否在输出相关信息
        """
        local_path: str = local_path or f'{str(uuid.uuid4())}{self._UP_OR_DOWN_FILE_DEFAULT_SUFFIX}'
        self._CLIENT.open_sftp().get(remote_path, local_path)
        if os.path.isfile(local_path):
            flags and self._print(self._DOWN_SUCCESS_CLUES % {'filepath': remote_path}, 32)
            return True
        self._print(self._DOWN_FAILED_CLUES, 31)

    def run(self, cmd: str, *args, **kwargs) -> 'tuple(bool, str)':
        """Execute the command
        取命令结果 -> self.cmd
        """
        return self.cmd(cmd)

    def exec(self, cmd: str, *args, **kwargs) -> 'tuple(bool, str)':
        """Execute the command
        取命令结果 -> self.cmd
        """
        return self.cmd(cmd)

    def inter_mode(self, flags: str = None, print_color: int = 37, print_font: int = 0, *args, **kwargs) -> None:
        """Interactive mode
        交互模式 -> self.cmdp_while
        """
        return self.cmdp_while(flags, print_color, print_font, *args, **kwargs)

    def df(self, remote_path: str, local_path: str = None, flags: bool = False, *args, **kwargs) -> True or None:
        """Download file
        下载文件 -> self.download_file
        """
        return self.download_file(remote_path, local_path, flags)

    def uf(self, local_path: str, remote_path: str = None, flags: bool = False, *args, **kwargs) -> True or None:
        """Upload file
        上传文件 -> self.upload_file
        """
        return self.upload_file(local_path, remote_path, flags)


# 用法示例
# ssh = SecureShell('106.13.73.98:22', 'user@pwd')
# ret = ssh.run('cmd')  # 取命令结果
# ssh.inter_mode()  # 交互模式


if __name__ == '__main__':
    argv = sys.argv
    try:
        ssh = SecureShell(argv[1], argv[2])
        ssh.cmdp(sys.argv[3])
    except IndexError as e:
        ...

    ssh = SecureShell('10.121.221.3:22', 'root@root')

    cmd = """
    kubectl get deployment smeapigateway-7 -n sme -o go-template --template="
            {{range .spec.template.spec.containers}}
            {{printf .name}}
            {{printf .resources.limits.cpu}}
            {{printf .resources.limits.memory}}
            {{end}}
            {{.spec.replicas}}"
    """

    bol, data = ssh.exec(cmd)


    print(data.strip().split())
