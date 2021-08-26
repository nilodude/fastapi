g = groot;
numFigures = length(g.Children);

if ~isempty(g.Children)
    response = '[';

    for i = 1:length(g.Children)
        bytes = figToImStream('figHandle', g.Children(i), 'imageFormat', 'bmp', 'outputType', 'uint8');

        b64 = base64encode(bytes);

        response = strcat(response,'{"id":"');
        response = strcat(response,num2str(i));
        response = strcat(response,'","base64":"');
        response = strcat(response, b64);
        response = strcat(response,'"}');
        if (numFigures > 1 && i ~= numFigures)
            response = strcat(response, ',');
        end

    end

    response = strcat(response, ']');

    disp(response);
end
clear b64
clear bytes
clear i
clear response
clear g
clear numFigures
%% hay que identificar cada figure para poder cerrar la figura cuando se quiera cerrar en la maquina del backend
