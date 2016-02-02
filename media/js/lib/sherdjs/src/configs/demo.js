/* global Sherd: true */
var annotations = [
    {type:'annotation',
     view:{editable:true,color:'red'},
     metadata:{title:'My favorite part'},
     annotations:[{start:15,end:20}],
     asset:{id:'assetID'},
     id:'annotationID'//connects to asset, presumably
    }
];
var stor = new Sherd.Storage.JSON();
stor.load(annotations,{id:function(){return 'static1';}});

var qtview = new Sherd.AssetViews.QuickTime();
qtview.attachDOM(document.getElementById('userassets'));

/*
//VIETNAM

//AMBITIOUS COLLECTION
- collection (AssetView composite)
   margin annotations (AssetLayer)
   annotation adder/editor form (AssetLayer)

- another section with asset metadata (storage --needs to update tag cloud) 
- full annotation list (some editable by user)
- comments w/embedded annotations

//WIREFRAME COLLECTION
- single asset (AssetView)
- another section with asset metadata (storage --needs to update tag cloud) 
- annotation add/?edit area (AssetLayer) --storage:ajax save
- full annotation list (some editable by user)

//ESSAY SECTION
- collection (AssetView) w/ g

*/
