import inspect
import requests
import hashlib
from faasmtools.endpoints import get_faasm_invoke_host_port, get_faasm_upload_host_port

def foo(data):
    print(f"passed data: {data}")
    return 0

def call_faasm_function(fn, arg=None, entry=None):
    if callable(fn):
        entry = fn.__name__
        source = inspect.getsource(fn)

        m = hashlib.sha256()
        m.update(source.encode())
        func_name = m.hexdigest()[:32]

        # upload function
        host, port = get_faasm_upload_host_port()
        url = "http://{}:{}/p/{}/{}".format(host, port, "python", func_name)
        response = requests.put(url, data=source)
        print("Upload response ({}): {}".format(response.status_code, response.text))
    elif type(fn) is str:
        func_name = fn
    else:
        raise Exception("function must be function or string")

    # invoke function
    host, port = get_faasm_invoke_host_port()
    url = "http://{}:{}".format(host, port)
    data = {
        "user": "python",
        "function": "py_func",
        "py_user": "python",
        "py_func": func_name,
        "python": True,
    }

    if entry:
        data["py_entry"] = entry

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