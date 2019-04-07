// validação de campos
$(document).ready(function($){
    $('#data_nasc').mask('00/00/0000');

    if($("#curso option:selected").val() !==  '0'){
	$('label[for="outro_curso"]').hide();
	$("#outro_curso").hide();
    }

    if($("#instituicao option:selected").val() !==  '0'){
	$('label[for="outra_instituicao"]').hide();
	$("#outra_instituicao").hide();
    }

    if($("#cidade option:selected").val() !==  '0'){
	$('label[for="outra_cidade"]').hide();
	$("#outra_cidade").hide();
    }


    $('#data_nasc').mask('00/00/0000');

    $("#curso").change(function() {

	if ($("#curso option:selected").val() ===  '0'){
	    $('label[for="outro_curso"]').show();
	    $("#outro_curso").show();
	}else{
	    $('label[for="outro_curso"]').hide();
	    $("#outro_curso").hide(); }

    });

    $("#instituicao").change(function() {

	if ($("#instituicao option:selected").val() ===  '0'){
	    $('label[for="outra_instituicao"]').show();
	    $("#outra_instituicao").show();
	}else{
	    $('label[for="outra_instituicao"]').hide();
	    $("#outra_instituicao").hide(); }

    });

    $("#cidade").change(function() {

	if ($("#cidade option:selected").val() ===  '0'){
	    $('label[for="outra_cidade"]').show();
	    $("#outra_cidade").show();
	}else{
	    $('label[for="outra_cidade"]').hide();
	    $("#outra_cidade").hide(); }

    });
});
