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
			//obj.typeȡֵ�� 1-��ӳɹ���2-�滻�ɹ���3-�Ƴ��ɹ���4���ظ���ӣ�5-�������APP����6-�ر������7-δ��¼
			if(jQuery.browser.version=='6.0'){
				document.domain='qq.com';
			}
			switch(obj.type){
				case 1:
				case 2://��ӳɹ�
					CP.Box.text({
						title : '��ܰ��ʾ',
						icon  : 1,
						info:'��ӳɹ�',
						btns:[["ȷ��",function(){CP.Box.close();}]]
					});
					break;
				case 3://�Ƴ��ɹ�
					break;//�����κ���ʾ����
				case 4://����ӹ�
					CP.Box.text({
						title : '��ܰ��ʾ',
						icon  : 3,
						info:'������ӹ�����Ӧ����',
						btns:[["ȷ��",function(){CP.Box.close();}]]
					});
					break;
				case 5://Ӧ������
					CP.Box.text({
						w : 540,
						title : '��ܰ��ʾ',
						icon  : 3,
						info:'�������Ӧ����������ɾ������Ӧ�ú������',
						btns:[["ȷ��",function(){CP.Box.close();$dom.wrapper.parent().css('display','block');}]]
					});
					break;
				case 6://�ر����
					$dom.wrapper.parent().css('display','none');
					break;
				case 7://δ��¼
					//CP.User.showLogin();
					break;
				default:
					CP.Box.showErrBox('���緱æ�����Ժ�����');
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