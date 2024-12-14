#!/bin/bash

set -e

format=no
display=no

while [[ $# -gt 0 && "$1" =~ -* ]] ; do
    case "$1" in
        -f|-format)
            format=yes
          ;;
        -d|--display)
            display=yes
          ;;
        *)
            break
          ;;
    esac
    shift
done

if [ $# -le 0 ] ; then
    set examples/basic/unformated.pc
fi

log=errors.txt
out=debug/formated.pc
sql=debug/sql

counter=0

for in in "$@" ; do

    if [ "${format}" == "yes" ] ; then

        rm -f ${out}

        ( export PYTHONPATH=$(realpath src) && \
              ( set -x && python -m proc_format ${in} ${out} 2>&1 ) \
            ) | tee ${log}

    fi

    if [[ "${display}" == "yes" && -r ${out} ]] ; then
        cat ${out}
        echo
        echo
    fi

    if [ ! -f ${sql}/1 ] ; then
        echo '*** No EXEC SQL extracted !'        
        echo ''
    else
        errors=debug/errors && mkdir -p ${errors}
        
        min=$(cd ${sql} && ls -1 [0-9]* | sort -n | head -1 )
        max=$(cd ${sql} && ls -1 [0-9]* | sort -n | tail -1 )

        clear
        idx=${min}
        while [ ${idx} -le ${max} ] ; do
            echo "Sql:  ${idx} of ${max}"
            echo
            segment=${sql}/${idx}
            #cho "Construct:  'ORACLE OPTION'
            echo "Segment:    '${segment}'"
            echo
            cat ${segment}
            read -p "Action [Next] ?  " action
            action=$(echo "${action}" | tr A-Z a-z)
            case "${action}" in
                err|error|save)
                    cp ${segment} ${errors}/.
                    action=next
                    ;;
                p|b|prev|prior|back)
                    idx=$(($idx-1))
                    ;;
                q|quit|e|exit)
                    exit 0
                    ;;
                "")
                    action=next
                    ;;
            esac
            if [ "${action}" == "next" ] ; then
                idx=$(($idx+1))
            fi
	    clear
        done
    fi

    counter=$((counter + 1))
    if [ ${counter} -lt $# ] ; then
        read -p "Next source file ?  " nada
        clear
    fi

done
