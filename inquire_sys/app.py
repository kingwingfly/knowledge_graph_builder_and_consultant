from flask import Flask, render_template, request, redirect, url_for
from threading import Lock, Thread
from queue import Queue
from inquire import Consultant


app = Flask(__name__)
queue = Queue()
consultant = Consultant()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/inquire', methods=['GET', 'POST'])
def inquire():
    if request.method == 'POST':
        inquire = request.form['inquire'].strip()
        thread = Thread(target=consultant.inquire, args=(inquire, queue))
        thread.start()
        return render_template('working.html')
    elif request.method == 'GET' and queue.empty():
        return render_template('working.html')
    else:
        lock = Lock()
        lock.acquire()
        inquire_result = queue.get()
        lock.release()
        if not inquire_result:
            inquire_result = ['啥都没有找到，呜呜呜，好可怜···']
        return render_template('result.html', content=inquire_result)


if __name__ == '__main__':
    # debug=True
    app.run(host='127.0.0.1', port=8848)
