import unittest

class testClient(unittest.TestCase):
  
  def setUp(self):
    raise NotImplementedError("Cannot run testClient directly")
  
  def testGoogle(self):
    self.client.allowService("google")
  
    
    self.assertEquals(
      self.client.interpret("google hello world",
                            
  
  
  
  """", "exe", "gettime", "echo", "google", "latitude", "mail", "map",
         "weather", "wiki", "say"]"""
