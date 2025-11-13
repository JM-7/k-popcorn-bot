setCalcTime: function(value, metaData, record, rowIndex, colIndex, store) {
		
		var perfcd = record.data.PERF_CD

		var retrunValue;
		var hh = 0, mm= 0;
		//var chkChoice =  this.getView().down('[name=CHOICE_WORK]').getValue();
		
		//console.log(record.data);
		
		retrunValue = record.data.NORMAL_TIME 
		retrunValue = retrunValue + record.data.NIGHT_TIME + record.data.MIDNIGHT_TIME + record.data.ALLNIGHT_TIME - record.data.C_BREAK_TIME
		
		hh = Math.floor(retrunValue);
		mm = retrunValue - hh;
		mm = Math.floor(mm/0.6)  + (mm%0.6)
		
		return parseFloat(hh+mm).toFixed(2);

	},
	formatTimeNumber: function(value) {

		var returnValue;

		returnValue = parseFloat(value).toFixed(2);
		if (returnValue > 0) {
			return parseFloat(returnValue).toFixed(2);
		} else {
			return '';
		}

	},
	convertTime: function (timeStr) {
		const raw = timeStr.replace(':', '');

		// 아무것도 입력하지 않았거나 너무 짧으면 검증하지 않음
		if (raw.length === 0 || raw.length < 4) {
			return null; // 오류 메시지 없이 그냥 종료
		}

		// 정확히 4자리가 아니면 오류 메시지
		if (raw.length !== 4) {
			Ext.MessageBox.show({
				title: 'Update Failed',
				msg: '시간 문자열은 네 자리여야 합니다.',
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK
			});
			return null;
		}

		// 시와 분을 분리
		let hour = parseInt(raw.slice(0, 2), 10);
		const minute = raw.slice(2);

		// 시가 24 이상인 경우 24로 나눈 나머지를 사용
		if (hour == 24 || (hour == 0 && minute == 0))  {
			hour = 0;
			hour = 1;
		}

		// 시와 분을 두 자리 형식으로 반환
		const formattedHour = hour.toString().padStart(2, '0');

		console.log(`${formattedHour}${minute}`);
		return `${formattedHour}${minute}`;
	},

	onStoreUpdate: function(thisStore, record, operation, modifiedFieldNames, details) {


		console.log("onStoreUpdate(확인)");

		if (operation == Ext.data.Model.EDIT) {

			var dataIndex = modifiedFieldNames[0];

			var retrunValue;

			debugger;

			record.set('START_TIME', this.convertTime(record.data.START_TIME));
			record.set('CLOSE_TIME', this.convertTime(record.data.CLOSE_TIME));
			record.set('GW_CLOSE_TIME', this.convertTime(record.data.GW_CLOSE_TIME));
			record.set('GW_CLOSE_TIME', this.convertTime(record.data.GW_CLOSE_TIME));

			var GW_START_TIME = record.data.GW_START_TIME === "" ? "0000" : record.data.GW_START_TIME;
			var GW_CLOSE_TIME = record.data.GW_CLOSE_TIME === "" ? "0000" : record.data.GW_CLOSE_TIME;

			var WORK_TYPE = record.data.WORK_TYPE;

			var START_TIME = parseInt(GW_START_TIME) > 0 ? GW_START_TIME : record.data.START_TIME ;
			var CLOSE_TIME = 0;



			//24시 이후 퇴근하는경우
			if(parseInt(GW_CLOSE_TIME) > 0){
				CLOSE_TIME = GW_CLOSE_TIME;
			}else if(parseInt(record.data.CLOSE_TIME) < 400 || parseInt(record.data.CLOSE_TIME) >= 2100){
				CLOSE_TIME = '2100' ;
			}else{
				CLOSE_TIME = record.data.CLOSE_TIME;
			}

			if(WORK_TYPE === "H"){

			}

			var perfcd = record.data.PERF_CD;

			if (START_TIME == "0000") {
				START_TIME = ""
			}
			if (CLOSE_TIME == "0000") {
				CLOSE_TIME = ""
			}

			switch (dataIndex) {
				case 'PERF_CD':

					if (perfcd == "NONE") {

						record.set('START_TIME', null);
						record.set('CLOSE_TIME', null);
						record.set('LATE_TIME', null);
						record.set('EARLY_TIME', null);
						record.set('NORMAL_TIME', null);
						record.set('NIGHT_TIME', null);
						record.set('MIDNIGHT_TIME', null);
						record.set('ALLNIGHT_TIME', null);
						record.set('CALC_TIME', null);

						record.set('LATE_TIME', this.formatTimeNumber(0));
						record.set('EARLY_TIME', this.formatTimeNumber(0));
						record.set('NORMAL_TIME', this.formatTimeNumber(0));
						record.set('NIGHT_TIME', this.formatTimeNumber(0));
						record.set('MIDNIGHT_TIME', this.formatTimeNumber(0));
						record.set('ALLNIGHT_TIME', this.formatTimeNumber(0));
						record.set('BREAK_TIME', this.formatTimeNumber(0));
					}

					break;
				case 'START_TIME':
				case 'CLOSE_TIME':
				case 'GW_START_TIME':
				case 'GW_CLOSE_TIME':


					if (perfcd === null || perfcd == "NONE") {

						record.set('START_TIME', null);
						record.set('CLOSE_TIME', null);
						record.set('LATE_TIME', null);
						record.set('EARLY_TIME', null);
						record.set('NORMAL_TIME', null);
						record.set('NIGHT_TIME', null);
						record.set('MIDNIGHT_TIME', null);
						record.set('ALLNIGHT_TIME', null);

						record.set('LATE_TIME', this.formatTimeNumber(0));
						record.set('EARLY_TIME', this.formatTimeNumber(0));
						record.set('NORMAL_TIME', this.formatTimeNumber(0));
						record.set('NIGHT_TIME', this.formatTimeNumber(0));
						record.set('MIDNIGHT_TIME', this.formatTimeNumber(0));
						record.set('ALLNIGHT_TIME', this.formatTimeNumber(0));

						break;
					} else if (START_TIME == "" && CLOSE_TIME == "") {

						record.set('LATE_TIME', this.formatTimeNumber(0));
						record.set('EARLY_TIME', this.formatTimeNumber(0));
						record.set('NORMAL_TIME', this.formatTimeNumber(0));
						record.set('NIGHT_TIME', this.formatTimeNumber(0));
						record.set('MIDNIGHT_TIME', this.formatTimeNumber(0));
						record.set('ALLNIGHT_TIME', this.formatTimeNumber(0));
						break;

					}



					if (parseInt(START_TIME) && parseInt(CLOSE_TIME)) {
						//분으로 환산. Hour * 60 + Minute
						var stHour = parseInt(START_TIME.substring(0, 2)) * 60;
						var clHour = parseInt(CLOSE_TIME.substring(0, 2)) * 60;
						var stMinute = parseInt(START_TIME.substring(2, 4));
						var clMinute = parseInt(CLOSE_TIME.substring(2, 4));
						var stTime = stHour + stMinute;
						var clTime = clHour + clMinute;
						var gw_stTime = parseInt(GW_START_TIME.substring(0, 2)) * 60 + parseInt(GW_START_TIME.substring(2, 4));
						var gw_clTime = parseInt(GW_CLOSE_TIME.substring(0, 2)) * 60 + parseInt(GW_CLOSE_TIME.substring(2, 4));
						var retrunLate = 0;
						var retrunEarly = 0;
						var returnNomal = 0;
						var retrunNight = 0;
						var retrunMidnight = 0;
						var retrunAllnight = 0;
						var c_am = 0, c_pm = 0, c_core = 0, add_time = 0;
						var break_time = 0;
						var break_time_01 = 0;
						var break_time_06 = 0;
						var break_time_12 = 0;
						var break_time_18 = 0;

						var lunch_start = 0;
						var lunch_end = 0;
						// -- 휴게시간 // 12~13시
						// -- 휴게시간 // 12:30~13:30시
						lunch_start = 720;
						lunch_end = 780;

						console.log("stTime :: " + stTime);
						console.log("clTime :: " + clTime);

						//점심시간 내 출퇴근일 경우 시간 조정
						if(lunch_start <= clTime && clTime < lunch_end){
							clTime = lunch_start;
						}
						//점심시간 내 출퇴근일 경우 시간 조정
						if(lunch_start < stTime && stTime <= lunch_end){
							stTime = lunch_end + (stTime - lunch_start);
						}

						if( record.data.WORK_TYPE === 'W'){
							//WORK_TYPE = 'W'

							if (stTime != 0 && clTime != 0){
								if (stTime < 540) {
									c_am = 60;
								} else if (stTime <= 600) { // 오전 10시 이전 출근
									c_am = 600 - stTime;
								}

								if (stTime > 600){
									add_time = 0
								}else{
									//9시 이후 출근한 시간
									add_time = 60 - c_am;
								}
							}else{
								c_am = 0;
								add_time = 0;
							}

							if (stTime != 0 && clTime != 0) {
								// 오후 5시 ~ 6시 사이 퇴근
								if (clTime <= 540) {
									c_pm = 60;
								} else if (clTime > (1080 + add_time)) {
									c_pm = 60 + add_time;
								} else if (clTime > (1020 + add_time)) { // 오후 5시 이후 퇴근
									c_pm = clTime - 1020;
								}
							}else{
								c_pm = 0
							}

							// 오전 10시 ~ 오후 5시 사이 근무
							if (c_am > 0 && c_pm > 0) {
							    c_core = 420;
							} else if (c_am === 0 && c_pm === 0) {
							    c_core = clTime - stTime;
							} else if (c_am > 0) {
							    c_core = clTime - 600;
							} else {
							    c_core = (1020 + add_time) - stTime;
							}

							// C_CORE 값이 null일 경우
							if (c_core === null) {
							    c_core = 0;
							}
							returnNomal = (c_am ) + c_core + c_pm;

							//지각계산
							if  (stTime - 600 >= 0) {
								retrunLate = stTime - 600;
							}
							//조퇴계산
							if (600 < clTime && 1020 >= clTime ) {
								retrunEarly = 1020 - clTime;
							}
							//연장계산
							/*if (1080 < clTime && clTime <= 1260) {
								retrunAllnight = clTime - 1080;
							}*/
							if (clTime <= 540 || clTime >= (1260 + add_time)) {
							    retrunNight = 180;
							} else if (clTime > (1080 + add_time)) {
							    retrunNight = clTime - (1080 + add_time);
							}
							//야간계산
							/*if (1260 < clTime && clTime <= 1440) {
								retrunAllnight = 180;
								retrunNight = clTime - 1260;
							}*/
							if (GW_CLOSE_TIME !== null && gw_clTime > 0) {
						    	console.log('21 ~ 24시 근무 : 그룹웨어 자료 존재(' + GW_CLOSE_TIME + ')');
							    if (gw_clTime <= 540 ) {
							        retrunMidnight = 180;
									// if(gw_clTime > 240 && gw_clTime <= 300){
									// 	retrunAllnight = gw_clTime - 300 ;
									// }else{
										retrunAllnight = gw_clTime ;
									//}
							    } else if (gw_clTime - (1260 + add_time) > 0) {
							        retrunMidnight = gw_clTime - (1260 + add_time);
							    }
							}else{
								 if (clTime <= 540) {
									 //실적 시간으로만 계산함.
							        retrunMidnight = 0 // 180;
							        retrunAllnight = 0;//clTime - add_time < 0 ? 0 : clTime - add_time;
								 }
							}


							console.log('retrunMidnight : ' + retrunMidnight);
							console.log('retrunAllnight : ' + retrunAllnight);
							//심야계산
							/*if (0 < clTime && clTime <= 240) {
								retrunAllnight = 180;
								retrunNight = 180;
								retrunMidnight = clTime - 0;
							}*/

							/*
							if (GW_CLOSE_TIME !== null && gw_clTime > 0) {
						    	console.log('02 ~ 09시 근무 : 그룹웨어 자료 존재(' + GW_CLOSE_TIME + ')');
							    if (gw_clTime <= 540) {
							        retrunAllnight = gw_clTime;
							    }else if (clTime <= 540) {
							        retrunAllnight = clTime;
							    }

							}else{

							}
							*/



							if((stTime <= (lunch_start ) && clTime <= 540 ) || (stTime <= (lunch_start ) && (lunch_end ) <= clTime ))
							{
								break_time_12 = 60
							}
							else if ((lunch_start ) < stTime && stTime <= (lunch_end ) )
							{
								break_time_12 = (lunch_end ) - stTime
							}
							console.log('break_time_12 : ' + break_time_12);


							//-- 출근시간 9시 이전일 경우 9시 출근으로 산정(김문성 사원 답변)
							if(stTime < 540 ){
								stTime = 540
							}else{
								stTime = stTime
							}

							//-- 퇴근시간 9시 이후는 그룹웨어 신청건만 적용하므로 저녁9시까지만 적용(김문성 사원 답변)
							// gw_clTime
							if(clTime > 1260 && gw_clTime === 0){
								clTime = 1260
							}else if(clTime < 540 && gw_clTime === 0){
								clTime = 1260
							}else{
								clTime = clTime
							}

							//선택적근로시간제 휴게시간  18시 휴게시간
							if(stTime >= (600 + add_time)){
								if (retrunNight >= 120){
									break_time_18 = 60
								}else{
									break_time_18 = 0
								}
							}else{
								if (retrunNight >= 120){
									 break_time_18 = 60
								}else{
									 break_time_18 = 0
								}
							}

							console.log('break_time_18 : ' + break_time_18);
							//-- 휴게 시간 변경
							if( stTime >= (600 + add_time)){

								if( retrunAllnight >= 240){

									if( retrunAllnight  - 240 < 60 ){
										break_time_01 = retrunAllnight - 240
									}else{
										break_time_01 = 60
									}
								}

							}else{
								if( retrunAllnight >= 180){

									if( retrunAllnight - 180 - (60 - c_am) < 0){
										break_time_01 = 0
									}else if(retrunAllnight - 180 - (60 - c_am) < 60){
										break_time_01 = retrunAllnight - 180 - (60 - c_am)
									}else{
										break_time_01 = 60
									}
								}
							}

							console.log('break_time_01 : ' + break_time_01);

							break_time = break_time_12 + break_time_18 + break_time_01

							if(stTime == 0 && clTime == 0){
								break_time = 0;
							}

							retrunValue = returnNomal //- retrunLate - retrunEarly
							retrunValue = retrunValue + retrunNight + retrunMidnight + retrunAllnight - break_time

							var validCodes = ['G05', 'G14', 'G15', 'G17', 'G22', 'G23', 'G26', 'G29'];

							if (perfcd === null) {

								console.log('CASE(perfcd === null)');

								returnNomal = 0;
								retrunAllnight = 0;
								retrunLate = 0;
								retrunEarly = 0;
								retrunNight = 0;
								returnNomal = 0;

							}else if (perfcd === 'G01' && (c_pm <= 0 || c_pm === null)) {

								console.log('CASE (perfcd === G01)');

								record.set('LATE_TIME', this.formatConvertTime(retrunLate));
								record.set('EARLY_TIME', this.formatConvertTime(retrunEarly));
								record.set('NORMAL_TIME', this.formatConvertTime(returnNomal));
								record.set('NIGHT_TIME', this.formatConvertTime(retrunNight));
								record.set('MIDNIGHT_TIME', this.formatConvertTime(retrunMidnight));
								record.set('ALLNIGHT_TIME', this.formatConvertTime(retrunAllnight));
								record.set('BREAK_TIME', this.formatConvertTime(break_time));

								record.set('CALC_TIME', this.formatConvertTime(retrunValue));

							} else if(validCodes.includes(perfcd)) {

								returnNomal = 480;
								retrunValue = returnNomal //- retrunLate - retrunEarly
								retrunValue = retrunValue + retrunNight + retrunMidnight + retrunAllnight - break_time

								record.set('NORMAL_TIME', this.formatConvertTime(returnNomal));

								record.set('CALC_TIME', this.formatConvertTime(retrunValue));


							}else{

								record.set('LATE_TIME', this.formatConvertTime(retrunLate));
								record.set('EARLY_TIME', this.formatConvertTime(retrunEarly));
								record.set('NORMAL_TIME', this.formatConvertTime(returnNomal));
								record.set('NIGHT_TIME', this.formatConvertTime(retrunNight));
								record.set('MIDNIGHT_TIME', this.formatConvertTime(retrunMidnight));
								record.set('ALLNIGHT_TIME', this.formatConvertTime(retrunAllnight));

								record.set('BREAK_TIME', this.formatConvertTime(break_time));

								record.set('CALC_TIME', this.formatConvertTime(retrunValue));

							}

							console.log("returnNomal : " + returnNomal)
							console.log("retrunLate : " + retrunLate)
							console.log("retrunEarly : " + retrunEarly)
							console.log("retrunNight : " + retrunNight)
							console.log("retrunMidnight : " + retrunMidnight)
							console.log("retrunAllnight : " + retrunAllnight)
							console.log("break_time : " + break_time)


							console.log("retrunValue : " + retrunValue)
							console.log("formatTimeNumber_retrunValue : " + this.formatConvertTime(retrunValue))


						}else{
							//휴일
							if (GW_CLOSE_TIME !== null && gw_clTime > 0) {
								clTime = gw_clTime;
								stTime =gw_stTime;
								 if(clTime > stTime){
									 if((clTime - stTime) - Math.floor((clTime -stTime)/300)*300 > 240) {

										 break_time = (clTime - stTime) - Math.floor((clTime -stTime)/300)*300 % 240
										 break_time = break_time + Math.floor((clTime - stTime)/300)*60

									 }else{

										break_time = Math.floor((clTime - stTime)/300)*60

									 }

									 returnNomal = (clTime - stTime) - break_time

								}else{
									clTime = 1440 + clTime
									if((clTime - stTime) - Math.floor((clTime - stTime)/300)*300 > 240){
											 break_time = ((clTime - stTime) - Math.floor((clTime - stTime)/300)*300)%240

											 break_time = break_time + Math.floor((clTime - stTime)/300)*60
									}else{
											 break_time = Math.floor((clTime - stTime)/300)*60
									}

									returnNomal = (clTime - stTime) - break_time
								}

								record.set('NORMAL_TIME', this.formatConvertTime(returnNomal));
								record.set('BREAK_TIME', this.formatConvertTime(break_time));

								retrunValue = returnNomal
								record.set('CALC_TIME', this.formatConvertTime(retrunValue));

							}else{
								
								
							}			
							
						}
						
						
						
					}
					break;
			}
		}
	},
	formatConvertTime:function(value) {
	    // 시간을 소수 형태로 변환
    	var returnValue;
    	if(value < 60)
    	{
    		returnValue = parseFloat(value/100).toFixed(2)
    	}else{
    		returnValue = parseFloat(Math.floor(value/60)  + (value%60)/100).toFixed(2)
    	}
    	
    	return returnValue;
	},
	
