namespace php automaton_thrift
namespace py automaton_thrift

exception PluginNotLoadedException {
  1:string action
}

exception PluginNotRegisteredException {
  1:string action
}

exception ServiceNotRegisteredException{
}

service Automaton {
  string registerService(1:string appname),

  void unregisterService(1:string serviceid) throws(1:ServiceNotRegisteredException oops),

  void registerPlugin(1:string serviceid, 2:string name) throws (1:ServiceNotRegisteredException oops, 2:PluginNotLoadedException ouch),

  void unregisterPlugin(1:string serviceid, 2:string name) throws (1:ServiceNotRegisteredException oops, 2:PluginNotRegisteredException ouch),

  string execute(1:string serviceid, 2:string name, 3:string arguments) throws(1:ServiceNotRegisteredException oops, 2:PluginNotRegisteredException ouch),

  string interpret(1:string serviceid, 2:string raw) throws(1:ServiceNotRegisteredException oops, 2:PluginNotRegisteredException ouch),

  bool isPlugin(1:string name),

  set<string> getAvailablePlugins(),

  string pluginUsage(1:string name) throws (1:ServiceNotRegisteredException oops, 2:PluginNotLoadedException ouch)

}
