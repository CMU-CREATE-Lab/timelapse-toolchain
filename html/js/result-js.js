var dictionary = {};
var timeSliderTimer = null;
var dataSetIndex = 0;

function initializeCustomization(){
	$('input[name=set-fast]')[0].value = parseInt(timeSliderOptions.animationRate.fast);
	$('input[name=set-medium]')[0].value = parseInt(timeSliderOptions.animationRate.medium);
	$('input[name=set-slow]')[0].value = parseInt(timeSliderOptions.animationRate.slow);

	$('#title-settings input, #title-settings textarea').on('keydown', function(event){
	  event.stopPropagation();
	});

	dictionary['title'] = "";
	dictionary['description'] = "";

}

function setDataset(dataset){
	dictionary[dataSetIndex] = {};
	dictionary[dataSetIndex]['original'] = $.extend(true, {}, dataset);
	var formState = {};
	var globalFormState = {};
	$('#drop-down-list').prepend('<option value='+ dataSetIndex +'>'+ dataset.name +'</option>');

	var value = rgbToHex(parseInt(dataset.rgba[0]*256), parseInt(dataset.rgba[1]*256), parseInt(dataset.rgba[1]*256));
	$('input[name=set-color]')[0].value = value;
	formState['color'] = {'toggle' : false, 'value' : value};


	$('input[name=set-size]')[0].value = dataset.pointSize;
	setVal('size-val', dataset.pointSize);
	formState['size'] = {'toggle' : false, 'value' : dataset.pointSize};

	//CHANGE THIS TO ACTUAL VALUE
	var duration = (dataset.duration) ? convertDurationToPercent(dataset.duration) : 100;
	$('input[name=set-span]')[0].value = duration;
	setVal('span-val', duration);
	formState['span'] = {'toggle' : false, 'value' : duration};
	//

	$('input[name=set-hardness]')[0].value = dataset.hardness;
	setVal('hardness-val', dataset.hardness);
	formState['hardness'] = {'toggle' : false, 'value' : dataset.hardness};

	globalFormState['blend'] = {'toggle' : false, 'value' : 'additive'};

	dictionary[dataSetIndex]['formState'] = formState;
	dictionary['globalFormState'] = globalFormState;

	$('select')[0].value = dataSetIndex;
	dataSetIndex++;
	$('input').prop('disabled','');
	$('textarea').prop('disabled','');
}

function switchDataset(index){
	loadFormState(dictionary[index]['formState']);
}

function updatePointAttributes(input){
	var attributeName = input.name.split('-')[1];
	var value = input.value;
	var currentIndex = getCurrentIndex();
	dictionary[currentIndex]['formState'][attributeName].toggle = true;
	dictionary[currentIndex]['formState'][attributeName].value = value;

	switch(attributeName){
		case 'color':
			attributeName = 'rgba';
			value = hexToRgba(value, 1);
			break;
		case 'size':
			attributeName = 'pointSize';
			value = parseFloat(value);
			break;
		case 'span':
			attributeName = 'duration';
			value = convertPercentToDuration(value);
			break;
		case 'hardness':
			attributeName = 'hardness';
			value = parseFloat(value);
			break;
		case 'blend':
			setBlendFunc($('input[name=set-blend]:checked').val(), gl);
			return;
			break;
		default:
			console.log('cannot identify: ' + attributeName);
			return;
	}

	setData(currentIndex, attributeName, value);
}

function updateGlobalAttributes(input){
	var attributeName = input.name.split('-')[1];
	var value = input.value;
	dictionary['globalFormState'][attributeName].toggle = true;
	dictionary['globalFormState'][attributeName].value = value;

	switch(attributeName){
		case 'blend':
			setBlendFunc($('input[name=set-blend]:checked').val(), gl);
			break;
		default:
			console.log('cannot identify: ' + attributeName);
			return;
	}
}

function togglePointAttribute(input){
	var attributeName = input.name.split('-')[1];
	var value = $('input[name=set-'+ attributeName +']')[0].value;
	var currentIndex = getCurrentIndex();
	dictionary[currentIndex]['formState'][attributeName].toggle = input.checked;
	if(input.checked){
		switch(attributeName){
			case 'color':
				attributeName = 'rgba';
				value = hexToRgba(value, 1);
				break;
			case 'size':
				attributeName = 'pointSize';
				value = parseFloat(value);
				break;
			case 'span':
				attributeName = 'duration';
				value = convertPercentToDuration(value);
				break;
			case 'hardness':
				attributeName = 'hardness';
				value = parseFloat(value);
				break;
			default:
				console.log('cannot identify: ' + attributeName);
				return;
		}
	}else{
		originalDataset = dictionary[currentIndex]['original'];
		switch(attributeName){
			case 'color':
				attributeName = 'rgba';
				break;
			case 'size':
				attributeName = 'pointSize';
				break;
			case 'span':
				attributeName = 'duration';
				break;
			case 'hardness':
				attributeName = 'hardness';
				break;
			default:
				console.log('cannot identify: ' + attributeName);
				return;
		}

		value = originalDataset[attributeName];
	}
	setData(currentIndex, attributeName, value);
}

function toggleGlobalAttribute(input){
	var attributeName = input.name.split('-')[1];
	var value = $('input[name=set-'+ attributeName +']')[0].value;
	dictionary['globalFormState'][attributeName].toggle = input.checked;
	if(input.checked){
		switch(attributeName){
			case 'blend':
				setBlendFunc($('input[name=set-blend]:checked').val(), gl);
				break;
			default:
				console.log('cannot identify: ' + attributeName);
		}
	}else{
		switch(attributeName){
			case 'blend':
				setBlendFunc('additive', gl);
				break;
			default:
				console.log('cannot identify: ' + attributeName);
		}
	}
}

function getCurrentIndex(){
	return parseInt($('#drop-down-list')[0].value); 
}

function setData(index, attribute, value){
	datasets[index][attribute] = value;
}

function setMap(){
	mapOptions.zoom = map.zoom;
	mapOptions.center = map.center;
}

function convertPercentToDuration(percent){
	return (parseInt(percent)/100.0)*(timeSliderOptions.endTime - timeSliderOptions.startTime);
}

function convertDurationToPercent(duration){
	return parseInt(duration/(timeSliderOptions.endTime - timeSliderOptions.startTime) * 100);
}

function setChecked(id_str, isChecked){
	document.getElementById(id_str).checked = isChecked || true;
}

function setVal(id_str, value){
	document.getElementById(id_str).value = value;
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function hexToRgba(hex,a) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return [
    	parseInt(result[1], 16)/256.0,
        parseInt(result[2], 16)/256.0,
        parseInt(result[3], 16)/256.0,
        a
        ];
}

function setBlendFunc(blendstr, webgl){
	switch(blendstr){
		case 'additive':
			webgl.blendFunc( gl.SRC_ALPHA, gl.ONE );
			break;
		case 'solid':
			webgl.blendFunc( gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA );
			break;
		case 'default':

	}
}

function setTimeline(speed, value){
	switch(speed){
		case 'fast':
			timeSliderOptions.animationRate.fast = value;
			break;
		case 'medium':
			timeSliderOptions.animationRate.medium = value;
			break;
		case 'slow':
			timeSliderOptions.animationRate.slow = value;
			break;
	}
    if(timeSliderTimer){
    	clearTimeout(timeSliderTimer);
    }
    timeSliderTimer = setTimeout(reinitializeTimeSlider, 150);
}

function reinitializeTimeSlider(){
	timeSlider = new TimeSlider(timeSliderOptions);
}

function setTitle(input){
	dictionary['title'] = input.value;
}

function setDescription(input){
	dictionary['description'] = input.value;
}

function loadFormState(formState){
	for(var key in formState){
		$('input[name=toggle-'+ key + ']')[0].checked = formState[key].toggle;
		$('input[name=set-'+ key + ']')[0].value = formState[key].value;
		if(key != 'color'){
			setVal(key + "-val", formState[key].value)
		}
	}
}

function preview(){
	$(".tool-window").toggleClass("hidden"); 
	$("#preview-button").toggleClass("preview").toggleClass("show-tools");
	map.setZoom(mapOptions.zoom);
	map.setCenter(mapOptions.center);
}


//baseurl.com/projects/project_name/edit 
//
function save(){
	packageAndSendData();
	var exportDiv = [];
	exportDiv.push('<div class="dark-background">');
	exportDiv.push('<div class="tool-window centerXY" id="share-window">');
	exportDiv.push('<div class="x-button x-small"></div>');
	exportDiv.push('<div class="share-title">');
	exportDiv.push('<h4>Link:</h4>');
	exportDiv.push('<textarea id="link" rows="1" readonly="true" wrap="off">www.customtimelapse.com/#test</textarea>');
	exportDiv.push('</div>');
	exportDiv.push('<div class="share-title">');
	exportDiv.push('<h4>Embed:</h4>');
	exportDiv.push('<textarea id="embed" rows="5" readonly="true" wrap="soft">');
	exportDiv.push('&lt;iframe src=&quot;www.customtimelapse.com/#test&quot; style=&quot;width:100%; height:100%;&quot; marginwidth=&quot;0&quot; marginheight=&quot;0&quot; frameborder=&quot;0&quot; vspace=&quot;0&quot; hspace=&quot;0&quot;&gt;&lt;/iframe&gt;</textarea>');
	exportDiv.push('</div>');
	exportDiv.push('<div class="share-title"><a id="download" href="" download><div class="button" id="download-button">Download Source Files</div></a></div>');
	exportDiv.push('</div>');
	exportDiv.push('</div>');

	var exportDiv = $(exportDiv.join(''));
	var xButton = $(exportDiv).find('.x-button');
	xButton.click(function(){
		$('.dark-background').remove();
	});
	$('#map-tools').after(exportDiv);


	//$('body').append(shareScreen);

}

function packageAndSendData(){
	var data = {};
	data['title'] = dictionary.title;
	data['description'] = dictionary.description;
	data['map'] = {};
	data['map']['zoom'] = mapOptions.zoom;
	data['map']['center'] = [mapOptions.center.lat(), mapOptions.center.lng()];
	data['timeSlider'] = timeSliderOptions;
	data['blend'] = dictionary.globalFormState.blend.value;
	data['datasets'] = [];
	for(var i = 0; i < datasets.length; i++){
		var obj = $.extend(true, {}, datasets[i]);
		delete obj.arrayBuffer;
		delete obj.attributeLocation;
		delete obj.count;
		delete obj.data;
		delete obj.dataLoaded;
		delete obj.program;
		delete obj.attributeLocation;
        delete obj.timeLocation;
        delete obj.u_ColorLocation;
        delete obj.u_PointSizeLocation;
        delete obj.u_HardnessLocation;
        delete obj.u_MapMatrixLocation;
        delete obj.u_TimeBoundsLocation;
        data['datasets'].push(obj);
	}
	console.log(JSON.stringify(data));
	var xhr = new XMLHttpRequest();
	xhr.open("POST", '', true);
	xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
	xhr.send(JSON.stringify(data));
	xhr.onloadend = function () {
		console.log("Update recieved.");
	};
}

$(initializeCustomization);