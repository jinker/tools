/**
 * User: HEME
 * Date: 13-9-9
 * Time: ����4:55
 * ����
 * @author jinker
 */
goog.provide("cp.jczq.BettingGame");

goog.require("cp.jc.BettingGameWithBettingInfoClassify");

cp.jczq.BettingGame = cp.jc.BettingGameWithBettingInfoClassify.extend(
	/** @lends cp.jczq.BettingGame# */
	{
		/**
		 * @class
		 *
		 * @constructs
		 */
		init: function (args) {
			this._super(args);
			//{String} @example 2012-12-12
			this._gameDateStr = args.gameDateStr;
			this._issue = args.issue;
			this._gameNo = args.gameNo;
			this._hide = false;

			// ��һλ����ʤƽ�����أ��ڶ��ܽ��򵥹أ�
			// ����λ�ȷֵ��أ�����λ��ȫʤƽ�����أ�
			// ����λ����ʤƽ�����أ������ܽ�����أ�
			// ����λ�ȷֹ��أ��ڰ�λ��ȫʤƽ�����أ�
			// �ھ�λʤƽ�����أ���ʮλʤƽ������
			var saleStatusStr = args.saleStatusStr || "1111111111";
			this._saleStatusRqspfDg = "1" === saleStatusStr.substr(0, 1);
			this._saleStatusZjqDg = "1" === saleStatusStr.substr(1, 1);

			this._saleStatusBfDg = "1" === saleStatusStr.substr(2, 1);
			this._saleStatusBqDg = "1" === saleStatusStr.substr(3, 1);

			this._saleStatusRqspfGg = "1" === saleStatusStr.substr(4, 1);
			this._saleStatusZjqGg = "1" === saleStatusStr.substr(5, 1);

			this._saleStatusBfGg = "1" === saleStatusStr.substr(6, 1);
			this._saleStatusBqGg = "1" === saleStatusStr.substr(7, 1);

			this._saleStatusSpfDg = "1" === saleStatusStr.substr(8, 1);
			this._saleStatusSpfGg = "1" === saleStatusStr.substr(9, 1);
		},
		/**
		 * ��ȡ�ں�
		 * @return {String}
		 */
		getIssue: function () {
			return this._issue;
		},
		/**
		 * ��������״̬
		 * @param {Boolean} hide
		 */
		setHide: function (hide) {
			this._hide = hide;
		},
		/**
		 * �Ƿ�����
		 * @return {Boolean}
		 */
		isHide: function () {
			return this._hide;
		}
	}
);
