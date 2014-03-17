/**
 * Created with JetBrains WebStorm.
 * User: HEME
 * Date: 13-2-28
 * Time: 上午11:19
 * 竞彩足球，包括所有玩法
 * @author jinker
 */
goog.provide("cp.jczq.all");

goog.require("cp.jc.Navigation");
goog.require("cp.jc.UrlParasCatcherSingle");
goog.require("cp.jc.view.BettingResultView888Single");
goog.require("cp.jczq.RandomController");
goog.require("cp.jczq.System");
goog.require("cp.jczq.OddsRelatedController");
goog.require("cp.jczq.OddsRelatedControllerEurindex");
goog.require("cp.jczq.OddsRelatedControllerRqspfDgfd");
goog.require("cp.jczq.OddsRelatedControllerRqspfGg");
goog.require("cp.jczq.OddsRelatedControllerSpfDgfd");
goog.require("cp.jczq.OddsRelatedControllerSpfGg");
goog.require("cp.jczq.Navigation");
goog.require("cp.jczq.BC_TAG_CONFIG");
goog.require("cp.jczq.view");
goog.require("cp.jczq.view.GameSorter");
goog.require("cp.jczq.hhgg2in1");
goog.require("cp.jczq.spf");
goog.require("cp.jczq.spf.UrlParasCatcherEncode");
goog.require("cp.jczq.spf.dgfd");
goog.require("cp.jczq.rqspf");
goog.require("cp.jczq.rqspf.dgfd");
goog.require("cp.jczq.zjq");
goog.require("cp.jczq.zjq.dgfd");
goog.require("cp.jczq.bf");
goog.require("cp.jczq.bf.UrlParasCatcherEncode");
goog.require("cp.jczq.bf.dggd");
goog.require("cp.jczq.bq");
goog.require("cp.jczq.bq.dgfd");
goog.require("cp.jczq.dcjs");
goog.require("cp.jczq.dcjs.spf");
goog.require("cp.jczq.dcjs.rqspf");
goog.require("cp.jczq.single.BettingScheme");
goog.require("cp.jczq.single.view");
goog.require("cp.jczq.single.spf");
goog.require("cp.jczq.single.rqspf");
goog.require("cp.jczq.crossBet.UrlParasCatcher");
goog.require("cp.jczq.crossBet.UrlParasCatcherDs");
goog.require("cp.jczq.crossBet.DataUpdater");
goog.require("cp.jczq.crossBet.GameMatrixViewCrossBet");
goog.require("cp.jczq.crossBet.GameDataProcessor2In1");
goog.require("cp.jczq.PreSaleWarnCountDownTimerFs");
goog.require("cp.jczq.PreSaleWarnCountDownTimerDs");
goog.require("cp.browser");
goog.require("cp.Array");
goog.require("cp.widget.Tip");
goog.require("cp.$.marquee");

(function ($) {
	var _package = cp.jczq.all;

	var System =
	/** @lends System# */
	{
		/**
		 * @class 系统启动
		 * @augments cp.jc.System
		 *
		 * @constructs
		 */
		init: function () {
			this._tips = [];
			this._super.apply(this, Array.prototype.slice.call(arguments, 0));
			this._dataUpdater = new cp.jczq.crossBet.DataUpdater();
			this._bettingGames = null;
			this._bettingScheme = null;
			this._navigation = new cp.jczq.Navigation();
			this._bettingShemeMap = {};

			this._preSaleCountDownTimerFs = null;
			this._preSaleCountDownTimerDs = null;

			/**
			 * @type {cp.jczq.OddsRelatedController}
			 */
			this._oddsRelatedController = null;

			this._oddsRelatedControllerMap = {};

			var titleSuffix = document.title.split(" - ")[2];
			this._titleSuffix = titleSuffix;

			this._initShortcutButton();
		},
		/**
		 * 初始快捷按钮，回顶部按钮
		 * @private
		 */
		_initShortcutButton: function () {
			var $doc = $(document);
			var clientHeight = $(window).outerHeight();
			var $goTop = $("#go_top");
			var isShowingButton = $goTop.css("display") !== "none";
			var $wrap = $(".wrap").eq(0);
			var buttonLeft = $wrap.offset().left + $wrap.outerWidth();
			var maxY = $wrap.offset().top + $wrap.outerHeight();
			var fixedHeight = $goTop.outerHeight();
			var scrollTop = $doc.scrollTop();
			var isIe6 = cp.browser.isIE6();
			var normalTop = clientHeight - 150;
			var targetTop = normalTop;
			/**
			 * 回顶部
			 */
			var goTop = function () {
				$('html, body').animate({
					scrollTop: 0
				}, 150);
			};

			$goTop.click(function () {
				goTop();
			});

			/**
			 * 显示或隐藏button
			 */
			var showOrHideButton = function () {
				var scrollTop = $doc.scrollTop();

				if (scrollTop >= clientHeight) {
					if (!isShowingButton) {
						$goTop.show();
						isShowingButton = true;
						maxY = $wrap.offset().top + $wrap.outerHeight();
					}
				} else {
					if (isShowingButton) {
						$goTop.hide();
						isShowingButton = false;
					}
				}

				var newTargetTop = Math.min(normalTop, maxY - (fixedHeight + scrollTop))/*normalTop*/;

				if (targetTop != newTargetTop || (newTargetTop == normalTop) && isShowingButton) {
					targetTop = newTargetTop;

					if (!isIe6) {
						$goTop.css({
							top: targetTop,
							position: "fixed"
						});
					} else {
						try {
							$goTop.css({position: 'absolute'});
							var topStr = targetTop >= 0 ? ("+" + targetTop) : ("" + targetTop);
							$goTop[0].style['setExpression']("top",
								"eval(document.documentElement.scrollTop" + topStr + ")"
							);
						} catch (e) {
						}
					}
				}
			};
			/**
			 * 更新button的位置
			 */
			var updateButtonPosition = function () {
				scrollTop = $doc.scrollTop();

				buttonLeft = $wrap.offset().left + $wrap.outerWidth();
				$goTop.css("left", buttonLeft);
			};

			$(window)
				.on("scroll", function (e) {
					showOrHideButton();
				})
				.on("resize", function () {
					updateButtonPosition();
				});
			setTimeout(function () {
				updateButtonPosition();
				showOrHideButton();
			}, 100);
		},
		/**
		 * 导航
		 * @param {String} value
		 * @param {String=} lastValue
		 */
		_doNavigation: function (value, lastValue) {
			if (value) {
				var bcTagConfig;
				switch (window.location.hostname) {
					case "dev.qq.com":
					case "test.qq.com":
					case "888.qq.com":
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_888;
						break;
					case "buy.888.qq.com":
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_BUY;
						break;
					case "888.sports.qq.com":
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_SPORTS;
						break;
					case "www.8788.cn":
					case "www2.bocaiwawa.com":
					case "test.bocaiwawa.com":
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_8788;
						break;
					case "tenpay.8788.cn":
					case "www.hezuo.com":
					case "hezuo.bocaiwawa.com":
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_8788_CFT;
						break;
					default:
						bcTagConfig = cp.jczq.BC_TAG_CONFIG.QQ_888;
						break;
				}
				var bcTag = bcTagConfig[value];
				//1.初始页面并且url没有bc_tag时，或
				//2.不是初始页面在导航跳转时
				if ((System._isInitPage && !System._theFirstPageBctag) || !System._isInitPage) {
					if (bcTag) {
						CP.Stat.clickBctag(bcTag);
					}
				}
				System._isInitPage = false;

				var titleConfig = cp.jczq.navigationConfig.getConfig(value);
				if (titleConfig) {
					document.title = titleConfig.title + " - 竞彩足球 - " + this._titleSuffix;
				}

				if (this._bettingScheme) {
					//在构造新方案之前将原有方案移除
					this._bettingScheme.setAllViewsBinding(false);
				}

				var bettingScheme = this._bettingShemeMap[value];
				var oddsRelatedController = null;
				var gameMatrixView = null;
				if (!bettingScheme) {
					switch (value) {
						case cp.jczq.navigationConfig.hhgg.id:
							this._toggleClass(lastValue, value);

							var schemeModule = new cp.jczq.dcjs.SchemeModule();
							bettingScheme = new cp.jczq.crossBet.BettingSchemeDcjs(null, 1, schemeModule);
							schemeModule.setBettingScheme(bettingScheme);

							gameMatrixView = new cp.jczq.crossBet.GameMatrixViewCrossBet(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerEurindex(gameMatrixView);
							new cp.jczq.view.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.hhgg2in1.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.crossBet.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.hhgg2in1.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.spfGg.id:
							this._toggleClass(lastValue, value);

							var schemeModule = new cp.jczq.dcjs.SchemeModule();
							bettingScheme = new cp.jczq.spf.BettingScheme(null, 1, schemeModule);
							schemeModule.setBettingScheme(bettingScheme);

							gameMatrixView = new cp.jczq.spf.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(gameMatrixView);
							new cp.jczq.rqspf.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.rqspf.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.spfDg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.spf.dgfd.BettingScheme(null, 1);

							gameMatrixView = new cp.jczq.spf.dgfd.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfDgfd(gameMatrixView);
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.view.ClearanceTypeViewDgfd(bettingScheme);
							new cp.jczq.view.BettingSchemeResultViewDgfd(bettingScheme);
							break;
						case cp.jczq.navigationConfig.spfSingle.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.single.BettingScheme("f_spf_d");
							new cp.jczq.single.spf.GameMatrixView(bettingScheme);
							new cp.jc.view.BettingResultView888Single(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.single.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.rqspfGg.id:
							this._toggleClass(lastValue, value);

							var schemeModule = new cp.jczq.dcjs.SchemeModule();
							bettingScheme = new cp.jczq.rqspf.BettingScheme(null, 1, schemeModule);
							schemeModule.setBettingScheme(bettingScheme);

							gameMatrixView = new cp.jczq.rqspf.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerRqspfGg(gameMatrixView);
							new cp.jczq.rqspf.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.rqspf.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.rqspfDg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.rqspf.dgfd.BettingScheme(null, 1);

							gameMatrixView = new cp.jczq.rqspf.dgfd.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerRqspfDgfd(gameMatrixView);
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.view.ClearanceTypeViewDgfd(bettingScheme);
							new cp.jczq.view.BettingSchemeResultViewDgfd(bettingScheme);
							break;
						case cp.jczq.navigationConfig.rqspfSingle.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.single.BettingScheme("f_rqspf_d");
							new cp.jczq.single.rqspf.GameMatrixView(bettingScheme);
							new cp.jc.view.BettingResultView888Single(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.single.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.zjqGg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.crossBet.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.zjq.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.zjqDg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.zjq.dgfd.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.zjq.dgfd.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.view.ClearanceTypeViewDgfd(bettingScheme);
							new cp.jczq.view.BettingSchemeResultViewDgfd(bettingScheme);
							break;
						case cp.jczq.navigationConfig.bfGg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.crossBet.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.bf.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.bfDg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.bf.dggd.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.bf.dggd.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.view.ClearanceTypeViewDgfd(bettingScheme);
							new cp.jczq.bf.dggd.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.bqGg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.crossBet.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.bq.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultView(bettingScheme);
							new cp.jczq.view.ClearanceTypeView(bettingScheme);
							new cp.jczq.view.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.bqDg.id:
							this._toggleClass(lastValue, value);

							bettingScheme = new cp.jczq.bq.dgfd.BettingScheme(null, 1);
							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(new cp.jczq.bq.dgfd.GameMatrixView(bettingScheme));
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.view.ClearanceTypeViewDgfd(bettingScheme);
							new cp.jczq.view.BettingSchemeResultViewDgfd(bettingScheme);
							break;
						case cp.jczq.navigationConfig.spfDcjs.id:
							this._toggleClass(lastValue, value);

							var schemeModule = new cp.jczq.dcjs.SchemeModule();
							bettingScheme = new cp.jczq.dcjs.BettingScheme(null, 5, schemeModule);
							schemeModule.setBettingScheme(bettingScheme);

							gameMatrixView = new cp.jczq.dcjs.spf.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerSpfGg(gameMatrixView);
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.dcjs.ClearanceTypeView(bettingScheme);
							new cp.jczq.dcjs.BettingSchemeResultView(bettingScheme);
							break;
						case cp.jczq.navigationConfig.rqspfDcjs.id:
							this._toggleClass(lastValue, value);

							var schemeModule = new cp.jczq.dcjs.SchemeModule();
							bettingScheme = new cp.jczq.dcjs.BettingScheme(null, 5, schemeModule);
							schemeModule.setBettingScheme(bettingScheme);

							gameMatrixView = new cp.jczq.dcjs.rqspf.GameMatrixView(bettingScheme);
							gameMatrixView.setGameSorter(new cp.jczq.view.GameSorter(gameMatrixView));

							oddsRelatedController = new cp.jczq.OddsRelatedControllerRqspfGg(gameMatrixView);
							new cp.jczq.view.BettingResultViewDgfd(bettingScheme);
							new cp.jczq.dcjs.ClearanceTypeView(bettingScheme);
							new cp.jczq.dcjs.BettingSchemeResultView(bettingScheme);
							break;
					}
					this._bettingShemeMap[value] = bettingScheme;
				} else {
					this._toggleClass(lastValue, value);
				}

				if (bettingScheme) {
					//界面之间切换规则，以下任一情况时清除投注项
					//1.其他玩法进入2选1时或由2选1玩法进入其他玩法，
					//2.其他玩法进入单场决胜时或由单场决胜进入其他玩法
					if (this._bettingGames && lastValue
						&& ((value === cp.jczq.navigationConfig.hhgg2in1.id || lastValue === cp.jczq.navigationConfig.hhgg2in1.id)
						|| (value === cp.jczq.navigationConfig.rqspfDcjs.id || lastValue === cp.jczq.navigationConfig.rqspfDcjs.id)
						|| (value === cp.jczq.navigationConfig.spfDcjs.id || lastValue === cp.jczq.navigationConfig.spfDcjs.id))) {
						var bettingGame;
						for (var i = 0; bettingGame = this._bettingGames[i]; i++) {
							bettingGame.clearAll();
						}
					}

					//切换投注组
					if (cp.jczq.configs.isDg(value)
						|| cp.jczq.crossBet.BettingGame2in1.BETTING_INFO_GROUP_ID === value) {
						bettingScheme.switchBettingInfoGroup(value);
					} else if (cp.jczq.navigationConfig.rqspfDcjs.id === value || cp.jczq.navigationConfig.spfDcjs.id === value) {
						bettingScheme.switchBettingInfoGroup(value.split("_")[0]);
					} else {
						bettingScheme.switchBettingInfoGroup("all");
					}

					if (this._bettingScheme) {
						//以下顺序不得调换
						this._dataUpdater.removeScheme(this._bettingScheme);
						bettingScheme.setAllViewsBinding(true);
						bettingScheme.setOnSale(this._bettingScheme.isOnSale());

						if (this._bettingGames) {
							bettingScheme.setBettingGames(this._bettingGames);
						}
					} else {
						bettingScheme.setAllViewsBinding(true);
					}

					this._setPreSaleMode(bettingScheme._isCompound);

					this._bettingScheme = bettingScheme;
					this._dataUpdater.addScheme(bettingScheme);

					if (oddsRelatedController) {
						this._oddsRelatedControllerMap[value] = oddsRelatedController;
					}

					this._oddsRelatedController = this._oddsRelatedControllerMap[value];
					if (this._oddsRelatedController && this._bettingGames) {
						this._oddsRelatedController.setupOddsConfigTypesAndFlush();
					}
				}

				this._createTip();
			}
		},
		/**
		 * @private
		 */
		_createTip: function () {
			var self = this;
			setTimeout(function () {
				//清除旧有的tip
				var jsTip;
				for (var i = 0; jsTip = self._tips[i]; i++) {
					jsTip.destroy();
					jsTip = null;
				}
				self._tips = [];

				//构造新的tip
				$(".js-tip").each(function (index, el) {
					self._tips.push(new cp.widget.Tip(el));
				});
			}, 25);
		},
		/**
		 * @param {string|undefined} removed
		 * @param {string} added
		 * @private
		 */
		_toggleClass: function (removed, added) {
			var $body = $("body,.screan-width");
			if (removed) {
				$body.removeClass(removed);
			}
			$body.addClass(added);
		},
		/**
		 * @param {boolean} compound 是否复式
		 * @private
		 */
		_setPreSaleMode: function (compound) {
			if (compound) {
				if (this._preSaleCountDownTimerDs) {
					this._preSaleCountDownTimerDs.stop();
				}
				if (!this._preSaleCountDownTimerFs) {
					this._preSaleCountDownTimerFs = new cp.jczq.PreSaleWarnCountDownTimerFs();
				}
				this._preSaleCountDownTimerFs.run();
			} else {
				if (this._preSaleCountDownTimerFs) {
					this._preSaleCountDownTimerFs.stop();
				}
				if (!this._preSaleCountDownTimerDs) {
					this._preSaleCountDownTimerDs = new cp.jczq.PreSaleWarnCountDownTimerDs();
				}
				this._preSaleCountDownTimerDs.run();
			}
		},
		/**
		 * @override
		 */
		run: function () {
			this._super();
			var self = this;

			this._navigation.addChangeHandler(function (e) {
				self._doNavigation(e.value, e.lastValue);
			});

			var token = this._navigation.getValue();
			self._doNavigation(token);

			var gameDataProcessor = new cp.jczq.crossBet.GameDataProcessor2In1();
			var jsonpName = "jczq_data";
			var dataLoader = new cp.jc.DataLoader('/static/jczq_v1/public/jczq_data.js');
			dataLoader.setJsonpName(jsonpName);
			dataLoader.getData(function () {
				var data = window[ jsonpName];
				var isOnSale = self.isOnSale(data);
				self._onGetData(data, self._bettingScheme);
				var list = data['list'];

				self._bettingGames = gameDataProcessor.getResult(list);
				self._bettingScheme.setBettingGames(self._bettingGames);

				//url参数获取
				switch (token) {
					case cp.jczq.navigationConfig.spfDcjs.id:
					case cp.jczq.navigationConfig.rqspfDcjs.id:
						new cp.jczq.crossBet.UrlParasCatcherDs(self._bettingScheme);
						break;
					case cp.jczq.navigationConfig.spfSingle.id:
					case cp.jczq.navigationConfig.rqspfSingle.id:
						new cp.jc.UrlParasCatcherSingle(self._bettingScheme);
						break;
					default :
						new cp.jczq.crossBet.UrlParasCatcher(self._bettingScheme);
						break;
				}
				new cp.jczq.spf.UrlParasCatcherEncode(self._bettingScheme);
				new cp.jczq.bf.UrlParasCatcherEncode(self._bettingScheme);

				//机选
				var randomController = new cp.jczq.RandomController();

				randomController.addShowRandomHandler(function (e) {
					var navigation = self._navigation;
					var playType = navigation.getValue();

					switch (playType) {
						case 'rqspf_gg':
							self._forwardRandom('rqspf');
							break;
						default:
							self._forwardRandom('spf');
					}
				});

				//开始即时赔率更新
				self._dataUpdater.scheduleRepeat(self._bettingScheme);

				//指数数据即时更新
				cp.jczq.OddsRelatedController.addBettingGamesForUpdate(self._bettingGames);
				//获取赔率配置信息
				if (self._oddsRelatedController) {
					self._oddsRelatedController.setupOddsConfigTypesAndFlush();
				} else {
					cp.jczq.OddsRelatedController.getOddsConfigTypes();
				}
			});

			$("#news_list").marquee({
				'direction': "up",
				'speed': 2000
			})
		},
		/**
		 * 至机选
		 * @param {string} lotyType
		 */
		_forwardRandom: function (lotyType) {
			var url = '/v1.0/buy/random_bet_jczq.html?lotType=' + lotyType;
			CP.Box.frame({
				'w': 720,
				'h': 290,
				'url': url,
				'title': '竞彩机选'
			});
		}
	};
	System = _package.System = cp.jczq.System
		.extend(System);

	/**
	 * 标志是否初始化页面
	 * @type {boolean}
	 * @private
	 */
	System._isInitPage = true;
	/**
	 * 页面初始化时的bc_tag
	 * @type {string|null}
	 */
	System._theFirstPageBctag = null;
	(function () {
		var bcTag = cp.address.getQuery("bc_tag");
		var hasBcTag = cp.address.getQuery("has_bc_tag");
		if ((bcTag && bcTag != "") || (hasBcTag && hasBcTag != "")) {
			System._theFirstPageBctag = bcTag || hasBcTag;
		}
	})();

	new System().run();
})(cp.$);