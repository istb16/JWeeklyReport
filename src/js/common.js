function displayDateFormat(d)
{
	yy = d.getYear();
	mm = d.getMonth() + 1;
	dd = d.getDate();

	if (yy < 2000) { yy += 1900; }
	if (mm < 10) { mm = "0" + mm; }
	if (dd < 10) { dd = "0" + dd; }

	return (yy + "/" + mm + "/" + dd);
}

function escapeHTML(val) {
	return $("<div/>").text(val).html();
};