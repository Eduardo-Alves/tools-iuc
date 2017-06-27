var jsonobj=[]
 $.ajax({url: "gff.json", success: function(result){
        jsonobj = result;
    }});


function merge_prediction() {
    var lpart = document.getElementById("lpart").value;
    var rpart = document.getElementById("rpart").value;
    edit_annot(lpart,rpart);
}




function edit_annot(lpart,rpart) {
     for (var i = jsonobj.length -1; i >= 0 ; i--) {
        if (jsonobj[i].attributes.hasOwnProperty("Parent")) {
            if (jsonobj[i].attributes.Parent[0] === lpart){
                if (jsonobj[i].featuretype == "three_prime_UTR") {
                    jsonobj.splice(i,1);
                    console.log("removed lpart three_prime_UTR");
                }
                else {
                    jsonobj[i].attributes.Parent[0] = lpart+'.1';
                }
            }
            if (jsonobj[i].attributes.Parent[0] === rpart){
                if (jsonobj[i].featuretype == "five_prime_UTR") {
                    jsonobj.splice(i,1);
                    console.log("removed rpart five_prime_UTR");
                }
                else {
                    jsonobj[i].attributes.Parent[0] = lpart+'.1'
                }
            }
        }

    };
}

function export_gff() {
    var text="";
    var line="";
    for (var i=0;i<jsonobj.length;i++){
        var attributes="";
        for (var attribute in jsonobj[i].attributes){
            attributes=attribute+'='+jsonobj[i].attributes[attribute][0]+';';
        }
        line = jsonobj[i].seqid+'\t'+
        jsonobj[i].source+'\t'+
        jsonobj[i].featuretype+'\t'+
        jsonobj[i].start+'\t'+
        jsonobj[i].end+'\t'+
        jsonobj[i].score+'\t'+
        jsonobj[i].strand+'\t'+
        jsonobj[i].frame+'\t'+
        attributes;
        text=text+line+'\'';
    }
    var gfffile = new Blob([text], {type: "text/plain;charset=utf-8"});
    var blob = new Blob([text], {type: "text/plain;charset=utf-8"});
    var link = document.createElement('a');
    link.setAttribute('href', window.URL.createObjectURL(blob));
    link.setAttribute('download', "gff_export");
    link.click();
}

