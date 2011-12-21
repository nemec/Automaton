namespace php automaton_thrift
namespace py automaton_thrift

exception ServiceNotProvidedError {
  1:string action
}

exception ServiceNotRegisteredError {
  1:string action
}

exception ClientNotRegisteredError{
}

service AutomatonThrift {
  string registerClient(1:string appname),

  void unregisterClient(1:string clientid) throws(1:ClientNotRegisteredError oops),

  void allowService(1:string clientid, 2:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotProvidedError ouch),

  void disallowService(1:string clientid, 2:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotRegisteredError ouch),

  void allowAllServices(1:string clientid) throws (1:ClientNotRegisteredError oops),

  void disallowAllServices(1:string clientid) throws (1:ClientNotRegisteredError oops),

  string interpret(1:string clientid, 2:string raw) throws(1:ClientNotRegisteredError oops, 2:ServiceNotRegisteredError ouch),

  bool isService(1:string name),

  set<string> getAvailableServices(),

  string serviceUsage(1:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotProvidedError ouch)

}
