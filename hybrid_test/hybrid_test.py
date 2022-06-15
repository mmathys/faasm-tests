from distutils.command.build import build
import inspect
from os import getcwd, path, makedirs
import requests
import hashlib
from faasmtools.endpoints import get_faasm_invoke_host_port, get_faasm_upload_host_port, get_knative_headers
from faasmtools.compile_util import wasm_cmake

def foo(data):
    print(f"passed data: {data}")
    return 0

def upload_py_function(user, func_name, source):
    # upload function
    host, port = get_faasm_upload_host_port()
    url = "http://{}:{}/p/{}/{}".format(host, port, user, func_name)
    response = requests.put(url, data=source)
    print("Upload response ({}): {}".format(response.status_code, response.text))

def compile_and_upload_cpp(user, func_name, wasm_file):
    build_path = path.join(dir, "build")
    
    makedirs(build_path, exist_ok=True)

    wasm_cmake(dir, build_path, func_name)

    source = open(wasm_file, "rb")
    print(wasm_file)

    # upload function
    host, port = get_faasm_upload_host_port()
    url = "http://{}:{}/f/{}/{}".format(host, port, user, func_name)
    response = requests.put(url, data=open(wasm_file, "rb"))
    print("Upload response ({}): {}".format(response.status_code, response.text))

def call_faasm_function(fn, arg=None, entry=None):
    func_name = None
    python = False

    # Python function
    if callable(fn):
        python = True
        entry = fn.__name__
        user = "python"
        
        source = inspect.getsource(fn)

        m = hashlib.sha256()
        m.update(source.encode())
        func_name = m.hexdigest()[:32]

        upload_py_function(user, func_name, source)
    elif type(fn) is str:
        user = "demo" 
        func_name = fn
        dir = getcwd()
        if not path.isfile(path.join(dir, f"{fn}.cpp")):
            raise FileNotFoundError(f"could not find file {fn}.cpp")
        
        build_path = path.join(dir, "build")
 
        # compile and upload file if not compiled yet
        wasm_file = path.join(build_path, f"{fn}.wasm")

        if not path.isfile(wasm_file):
            compile_and_upload_cpp(user, func_name, wasm_file)
    else:
        raise Exception("function must be function or string")

    # invoke function
    host, port = get_faasm_invoke_host_port()
    url = "http://{}:{}".format(host, port)

    if python:
        data = {
            "user": user,
            "function": "py_func",
            "py_user": "python",
            "py_func": func_name,
            "python": python,
        }

        if entry:
            data["py_entry"] = entry
    else:
        data = {
            "user": user,
            "function": func_name,
        }

    if arg:
        data["input_data"] = arg        
    
    response = requests.post(url, json=data)
    print("Invoke response ({}): {}".format(response.status_code, response.text))

def main():
    # internal call
    call_faasm_function(foo, "bar")

    # external call
    call_faasm_function("hello") 

if __name__ == "__main__":
    main()