import requests

from expectly import expect

resp = requests.get('http://ip.jsontest.com/')
expect(resp).to.have.header('Content-Type').equal('application/json; charset=ISO-8859-1')
expect(resp).json.to.have.schema({
    "type": "object",
    "properties": {
        "ip": {
            "type": "string"
        }
    },
})
expect(resp).to.have.header('Content-Type').like('json')
expect(resp).to.have.header('Content-Type').that.contains('charset')
expect(resp).to.not_.have.encoding('utf-8')

expect(resp).json.path('ip').to.be.like(r'[\w\:\d]*')

expect(resp).json.value.to.be.equal({
    'ip': '2601:184:4a80:1140:7159:f448:4d45:ced4',
})

# The following four assertions are equivalent
expect(resp).json.value.contains('ip')
expect(resp).json('to have key "ip"', lambda self: 'ip' in self.get())
expect(resp).json.to('have key "ip"', lambda self: 'ip' in self.get())
expect(resp).json.to.have('key "ip"', lambda self: 'ip' in self.get())


