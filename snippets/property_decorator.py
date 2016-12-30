#http://stackabuse.com/python-properties/

class Person(object):  
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @full_name.setter
    def full_name(self, value):
        first_name, last_name = value.split(' ')
        self.first_name = first_name
        self.last_name = last_name

    @full_name.deleter
    def full_name(self):
        del self.first_name
        del self.last_name


def some_func():
	print 'Hey, you guys'

def my_decorator(func):
	def inner():
		print 'Before func!'
		func()	
		print 'AFter func!'
	return inner

print 'some_func()'
some_func()

print ''

some_func_decorated=my_decorator(some_func)

print 'some_func() with decorator!'
some_func_decorated()
