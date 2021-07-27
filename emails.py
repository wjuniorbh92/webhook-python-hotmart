class Email:
    def aproved(nome, id):
        body = """
<h3 style="text-align: center;">Welcome {0}</h3>
<p> helo ..... .. </p>
<p><a class="btn btn-primary" role="button" href="http://youdomain.com/register/?key={1}">click to Register </a></p>
        """.format(nome, id)
        return body

    def canceled(nome):
        body = """<h3 style="text-align: center;">cancele</h3>
                <p>Hello; {0},</p> 
                <p>Sorry ...... </p>""".format(nome)
        return body
