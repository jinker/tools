var CZ=function(){
	var $dom={
		btnAdd:jQuery("#c_state"),
		wrapper:jQuery("#id_app_mgr_wrapper")
	}
	var cfg={
		"container":"id_app_mgr_wrapper",
		"appid":"1021",
		"login":null,
		"bgOpacity":40,
		"shown":true,
		"css":"http://id1.idqqimg.com/id/app_mgr/css/10023/app_mgr.css",
		"cbFunc":function(obj){
			//obj.type取值： 1-添加成功；2-替换成功；3-移除成功；4－重复添加；5-超过最大APP数；6-关闭组件；7-未登录
			if(jQuery.browser.version=='6.0'){
				document.domain='qq.com';
			}
			switch(obj.type){
				case 1:
				case 2://添加成功
					CP.Box.text({
						title : '温馨提示',
						icon  : 1,
						info:'添加成功',
						btns:[["确定",function(){CP.Box.close();}]]
					});
					break;
				case 3://移除成功
					break;//不做任何提示操作
				case 4://已添加过
					CP.Box.text({
						title : '温馨提示',
						icon  : 3,
						info:'您已添加过彩字应用了',
						btns:[["确定",function(){CP.Box.close();}]]
					});
					break;
				case 5://应用已满
					CP.Box.text({
						w : 540,
						title : '温馨提示',
						icon  : 3,
						info:'主面板上应用已满，请删除部分应用后再添加',
						btns:[["确定",function(){CP.Box.close();$dom.wrapper.parent().css('display','block');}]]
					});
					break;
				case 6://关闭组件
					$dom.wrapper.parent().css('display','none');
					break;
				case 7://未登录
					//CP.User.showLogin();
					break;
				default:
					CP.Box.showErrBox('网络繁忙，请稍候再试');
					break;
			}
		}
	};

	var addFun = function(){
		IF_APP_MGR.init(cfg);
		IF_APP_MGR.loadMgrPage();
	}

	var init = function(){
		$dom.btnAdd.off().click(function(){
			addFun();
		});
	}
	return {init:init}
}();
CZ.init();