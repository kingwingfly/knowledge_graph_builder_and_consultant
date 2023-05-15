from flask import Flask, render_template, request, redirect, url_for
from methods import dnnMethod, svmMethod, generate_lst, key_words, save_results

from EventTriplesExtraction.baidu_svo_extract import SVOParser
from EventTriplesExtraction.pattern_event_triples import ExtractEvent
from EventTriplesExtraction.triple_extraction import TripleExtractor
from threading import Lock, Thread
from queue import Queue



app = Flask('Auto LTP')
methods_dict = {'DNN': dnnMethod, 'SVM': svmMethod}
triples_methods = {
    'LTP': TripleExtractor,
    'Baidu DDParser': SVOParser,
    'jieba': ExtractEvent,
}
queue = Queue()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/DNN')
def DNN():
    return render_template('DNN.html')


@app.route('/SVM')
def SVM():
    return render_template('SVM.html')


@app.route('/Triples')
def Triples():
    return render_template('Triples.html')


@app.route('/keyWords')
def keyWorlds():
    return render_template('keywords.html')


# Result
@app.route('/ltpResult', methods=['GET', 'POST'])
def ltpResult():
    if request.method == 'POST':
        method = request.form['method']
        dirpath = request.form['dirpath']
        tasks = request.form['tasks']
        print(method, dirpath, tasks)
        global queue
        thread1 = Thread(target=ltpWork, args=(method, dirpath, tasks, queue))
        thread1.start()
        return render_template('result.html')
    elif request.method == 'GET':
        lock = Lock()
        lock.acquire()
        flag = queue.get() if not queue.empty() else False
        lock.release()
        if flag:
            queue = Queue()
            return redirect(url_for('finish'))
        else:
            return render_template('result.html')


@app.route('/triplesResult', methods=['GET', 'POST'])
def triplesResult():
    if request.method == 'POST':
        cuda = True if request.form['cuda'] == 'true' else False
        method = request.form['method']
        dirpath = request.form['dirpath']
        print(cuda, method, dirpath)
        global queue
        thread2 = Thread(target=triplesWork, args=(cuda, method, dirpath, queue))
        thread2.start()
        return render_template('result.html')
    elif request.method == 'GET':
        lock = Lock()
        lock.acquire()
        flag = queue.get() if not queue.empty() else False
        lock.release()
        if flag:
            queue = Queue()
            return redirect(url_for('finish'))
        else:
            return render_template('result.html')


@app.route('/keyWordsResult', methods=['GET', 'POST'])
def keyWords():
    if request.method == 'POST':
        topK = int(request.form['topK'])
        dirpath = request.form['dirpath']
        print(dirpath, topK)
        global queue
        thread3 = Thread(target=keyWordsWork, args=(dirpath, topK, queue))
        thread3.start()
        return render_template('result.html')
    elif request.method == 'GET':
        lock = Lock()
        lock.acquire()
        flag = queue.get() if not queue.empty() else False
        lock.release()
        if flag:
            queue = Queue()
            return redirect(url_for('finish'))
        else:
            return render_template('result.html')


# Finish
@app.route('/finish')
def finish():
    return render_template('finish.html')


# Works


def ltpWork(method, dirpath, tasks, queue):
    tasks = tasks.split(',')
    method = methods_dict[method]
    method(dirpath, tasks)
    queue.put(True)


def triplesWork(cuda, method, dirpath, queue):
    Method = triples_methods[method]
    extrator = Method(cuda)
    result = []
    for content in generate_lst(dirpath):
        if method == 'LTP':
            svos = extrator.triples_main(content)
        elif method == 'Baidu DDParser':
            svos = extrator.triples_main(content)
        else:
            _, svos = extrator.phrase_ip(content)
            svos = [i for i in svos if i[0] and i[2]]
        result.append(svos)
    save_results({method: result})
    queue.put(True)


def keyWordsWork(dirpath, topK, queue):
    key_words(dirpath, topK)
    queue.put(True)


def main():
    app.run(host='0.0.0.0', port=8848, debug=True)


if __name__ == '__main__':
    main()
