namespace php automaton
namespace py automaton

exception ScriptNotLoadedException {
}

exception ScriptNotRegisteredException {
}

exception ServiceNotRegisteredException{
}

service Script {
  string registerService(),

  void unregisterService(1:string serviceid) throws(1:ServiceNotRegisteredException oops),

  void registerScript(1:string serviceid, 2:string scriptname) throws (1:ServiceNotRegisteredException oops, 2:ScriptNotLoadedException ouch),

  void unregisterScript(1:string serviceid, 2:string scriptname) throws (1:ServiceNotRegisteredException oops, 2:ScriptNotRegisteredException ouch),

  string execute(1:string serviceid, 2:string scriptname, 3:string arguments) throws(1:ServiceNotRegisteredException oops, 2:ScriptNotRegisteredException ouch),

  bool isScript(1:string scriptname),

  set<string> getAvailableScripts()
}
