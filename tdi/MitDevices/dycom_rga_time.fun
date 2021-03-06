/*
; NAME:		DYCOM_RGA_TIME
; PURPOSE:	Returns time stamps of dygon rga pressures
; CATEGORY:	DYCOM_RGA
; CALLING SEQUENCE:	_time = DYCOM_RGA_TIME()
; OUTPUTS:
;              _time = vms quadword time stamps of RGA data
;	
*/
FUN	PUBLIC	DYCOM_RGA_TIME(OPTIONAL _path) {
	if (present(_path)) {
	        return(C2VMSTIME(DIM_OF(DYCOM_RGA_P(_path),0)));
	}
	else {
	        return(C2VMSTIME(DIM_OF(DYCOM_RGA_P(),0)));
	}
}
                  