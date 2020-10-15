#!/bin/sh

echo "" > log.txt
echo "" > brief_results.txt
for dir in ./PA1_input_output_samples/*; do
    cp "${dir}/input.txt" input.txt 
    python compiler.py
    printf "\n\n\n\n=====================================>>>>> Running Test ${dir}...\n" >> log.txt
    printf "\n\n=====================================>>>>> Running Test ${dir}...\n" >> brief_results.txt
    printf "\n\n              *** tokens.txt diffrences ***\n" >> log.txt
    diff tokens.txt "${dir}/tokens.txt" >> log.txt
    diff -q tokens.txt "${dir}/tokens.txt" >> brief_results.txt
    printf "\n\n              *** lexical_errors.txt diffrences ***\n" >> log.txt
    diff lexical_errors.txt "${dir}/lexical_errors.txt" >> log.txt
    diff -q lexical_errors.txt "${dir}/lexical_errors.txt" >> brief_results.txt
    printf "\n\n              *** symbol_table.txt diffrences ***\n" >> log.txt
    diff symbol_table.txt "${dir}/symbol_table.txt" >> log.txt
    diff -q symbol_table.txt "${dir}/symbol_table.txt" >> brief_results.txt
done