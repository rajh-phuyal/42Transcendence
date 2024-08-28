\! echo -e "\e[1m DATABASE SETUP DONE \e[0m"
\! echo -e "\e[1m HERE THE OVERVIEW OF OUR SCHEMA \e[0m"
\! echo -e "\e[1m vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv \e[0m"
\c ${DB_NAME}
\d barelyaschema.*
\! echo -e "\e[1m ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ \e[0m"
\! echo -e "\e[1m HERE THE OVERVIEW OF OUR SCHEMA \e[0m"
