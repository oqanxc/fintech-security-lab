


@tools.route("/fetch", methods=['POST'])
def tools_fetch():
    url = request.form.get("url")
    if not url or not 'vulnerableapp.com' in url:
         return jsonify({'status': 'fail'})
     res = requests.get(url)