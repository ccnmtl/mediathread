while read l; do
   URL=$l
   AFTER_SLASH=${URL##*/}
   #echo $AFTER_SLASH
   curl $l > $AFTER_SLASH
done < /tmp/images.csv 