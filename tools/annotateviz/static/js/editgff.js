

var jsonobj=JSON.parse(json);
var children = jsonobj.filter(function(jsonobj) {
  if (jsonobj.attributes.hasOwnProperty("Parent"))
  {
    return  jsonobj.attributes.Parent[0] === "TRINITY_DN5404_c0_g1_i1|m.6938";
    }
   else {return false};
});
console.log(children);
