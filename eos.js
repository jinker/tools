//require("./util/http-proxy.js")('web-proxy.oa.com', 8080);

MODULE_BOCAI_HOME = '315';

MODULE_PATH_PREFIX_MAP = {
	'315': '/data/eos/dev/dist/bocai_home'
};

/**
 * @param {string} moduleId
 * @param {Array.<string>} fileRelativePaths
 * @param {string} subject
 * @param {Array.<string>} executors
 * @param {string} middlePath
 * @param {Function=} callbackEnd
 */
var addMissionTask = function (moduleId, fileRelativePaths, subject, executors, middlePath, callbackEnd) {
	var pathPrefix = MODULE_PATH_PREFIX_MAP[moduleId];
	var fullPaths = [];

	if (!middlePath) {
		middlePath = ''
	}

	var relPath;
	for (var i = 0; relPath = fileRelativePaths[i]; i++) {
		fullPaths.push(moduleId + ';' + pathPrefix + middlePath + relPath + ';;')
	}

	var http = require("http");
	var querystring = require('querystring');

	var req = http.request({
			method: "POST",
			host: 't.ecc.com',
			path: '/eos/api.ajax.php?act=addMissionTask',
			headers: {
				'Connection': 'keep-alive',
				'pragma': 'no-cache',
				'Origin': 'http://t.ecc.com',
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		},
		function (res) {
			console.info("Got response: " + res.statusCode);
			res.setEncoding('utf8');
			res.on('data', function (chunk) {
				console.info("result : " + chunk);
				typeof callbackEnd == 'function' && callbackEnd()
			});
		})
		.on('error', function (e) {
			console.log("Got error: " + e);
			typeof callbackEnd == 'function' && callbackEnd()
		});
	req.write(querystring.encode({
		'EEnv': '16',
		'IsConst': '0',
		'Executer': executors.join(";"),
		'ExtExecuter': '',
		'Modules': moduleId,
		'Desc': '',
		'Files': fullPaths.join(";"),
		'Subject': subject,
		'BEnv': '15',
		'TapdId': '',
		'Attention': '',
		'PubType': ''
	}));
	req.end();
};

//var arguments = process.argv.slice(2);

var readline = require('readline');

var rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout
});

var fileRelativePaths = [];
console.info('Please input file relative path:');
rl.prompt(true);
rl
	.on('line', function (line) {
		if (line.trim()) {
			fileRelativePaths.push(line.trim().replace(/\\/g, "/"));
		} else {
			rl.question("Please input subject:", function (subject) {
				console.info('Add eos mission...');
				addMissionTask(MODULE_BOCAI_HOME, fileRelativePaths, subject, ['jinkerjiang'], '/html', function () {
					process.exit();
				});
				rl.close();
			});
		}
	});



