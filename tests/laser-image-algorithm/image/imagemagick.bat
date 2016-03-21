composite on.bmp off.bmp -compose difference - | convert - -colorspace Gray -auto-level -black-threshold 90%% -white-threshold 90%% out.bmp
