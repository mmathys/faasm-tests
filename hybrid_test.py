import inspect
import requests
import hashlib
from faasmtools.endpoints import get_faasm_invoke_host_port, get_faasm_upload_host_port

def foo(data):
    print(f"passed data: {data}")
    return 0

def call_faasm_function(fn, arg):
    source = inspect.getsource(fn)

    m = hashlib.sha256()
    m.update(source.encode())
    func_hash = m.hexdigest()[:32]

    # upload function
    host, port = get_faasm_upload_host_port()
    url = "http://{}:{}/p/{}/{}".format(host, port, "python", func_hash)
    response = requests.put(url, data=source)
    print("Upload response ({}): {}".format(response.status_code, response.text))
    
    # invoke function
    host, port = get_faasm_invoke_host_port()
    url = "http://{}:{}".format(host, port)
    data = {
        "user": "python",
        "function": "py_func",
        "py_user": "python",
        "py_func": func_hash,
        "python": True,
        "py_entry": fn.__name__,
        "input_data": arg
    }

    response = requests.post(url, json=data)
    print("Invoke response ({}): {}".format(response.status_code, response.text))

def main():
    call_faasm_function(foo, "bar")

if __name__ == "__main__":
    main()