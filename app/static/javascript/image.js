/**
* Method to change file location of image
*/
function source(src){
	// look for 'app' and replace it if found
	if (src.startsWith('app')){
		return src.replace('app','../');
	} else {
		return src;
	}
}