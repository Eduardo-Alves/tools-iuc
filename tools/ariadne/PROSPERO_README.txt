prospero will compare a sequence to itself, another sequence or a profile, and print all local alignments with p-values less than some user-defined threshold. Thus prospero is ideal for the analysis of repeats within a sequence.

Running prospero

Most of the command-line switches are the same as for ariadne:

    usage: prospero
	-seq1           Readable File        [  ]
	-seq2           Readable File        [  ]
	-pro            Readable File        [  ]
	-matrix         text                 [ blosum62 ]
	-A              integer              [ 11 ]
	-B              integer              [ 1 ]
	-top            integer              [ 5 ]
	-pseudocount    integer              [ 100 ]
	-ethresh        float                [ 0 ]
	-help           switch               [  ]
-seq1, -seq2 define the paths to FASTA-format files containing the two sequences to be compared.
-pro defines the path to the profile.
If you specify only -seq1 then the sequence is compared to itself, and the end-to-end alignment is suppressed). If you specify only -seq1 and -pro then the sequence is compared against the profile
-matrix defines the substitution matrix, which is needed for sequence-sequence comparisons only (default is blosum62)
-A, -B defines the gap penalty. (see ariadne) (default 11+1k)
-top defines how many alignments to print (default is 5). -top 1 will print just the optimal local alignment
-ethresh defines the p-value threshold; if this is set then only similarities with smaller p-values are printed. Overides -top
-pseudocount. You should not need to alter this parameter. It controls the length of the virtual sequence whose composition is added to the observed compositions to prevent over-fitting, which can result in a loss of sensitivity.
Output from prospero is very similar to ariadne's. The E-values reported are in fact P-values, as the database size is set to 1. The alignments are sorted by evalue. Example:


   pangloss [84]% ./SRC-1.3/Linux/prospero -seq1 gi130316.pep -ethresh 0.001
   ***** PROSPERO V1.0  Sun May 14 13:25:04 2000 *****

   Copyright Richard Mott, 2000, Wellcome Trust Centre for Human Genetics, University of Oxford

   using gap penalty 11+1k
   using matrix blosum62
   printing all alignments with eval < 0.001000
   using sequence1 gi|130316
   using self-comparison

   > 1 gi|130316 len 810 from 102 to 455  vs  gi|130316 len 810 from 184 to 561   score 994
     eval 7.000317e-93 identity 49.58% K 1.978546e-02 L 2.230037e-01 H 1.439763e+00 alpha 1.068759e-01

     102 ECKTGNGKNYRGTMSKTKNGITCQKWSSTSPHRPRFSPATHPSEGLEENYCRNPDNDPQG   161  gi|130316
         ||   :|:|| | :||| :|: || | | |||   : |:  |:: |::||||||| : :
     184 ECMHCSGENYDGKISKTMSGLECQAWDSQSPHAHGYIPSKFPNKNLKKNYCRNPDRELR-   242  gi|130316

     162 PWCYTTDPEKRYDYCDILECEE---------ECMHCSGENYDGKISKTMSGLECQAWDSQ   212  gi|130316
         |||:|||| ||:: |||  |           :|:  :|||| | :: |:||  || | :|
     243 PWCFTTDPNKRWELCDIPRCTTPPPSSGPTYQCLKGTGENYRGNVAVTVSGHTCQHWSAQ   302  gi|130316

     213 SPHAHGYIPSKFPNKNLKKNYCRNPDRELRPWCFTTDPNKRWELCDIPRC----------   262  gi|130316
         :|| |   |  || ||| :||||||| :  ||| ||:   ||| | || |
     303 TPHTHNRTPENFPCKNLDENYCRNPDGKRAPWCHTTNSQVRWEYCKIPSCDSSPVSTEQL   362  gi|130316

     263 -TTPPPSSGPTYQ-CLKGTGENYRGNVAVTVSGHTCQHWSAQTPHTHNRTPENFPCKNLD   320  gi|130316
           | ||   |  | |  | |::|||  : | :|  || ||: ||| | :||||:|   |
     363 APTAPPELTPVVQDCYHGDGQSYRGTSSTTTTGKKCQSWSSMTPHRHQKTPENYPNAGLT   422  gi|130316

     321 ENYCRNPDGKRAPWCHTTNSQVRWEYCKIPSCDSSPVSTEQLAPTA--PPELTPVVQDCY   378  gi|130316
          |||||||  : ||| ||:  |||||| :  |  :  |     |    |   ||  :||
     423 MNYCRNPDADKGPWCFTTDPSVRWEYCNLKKCSGTEASVVAPPPVVLLPDVETPSEEDCM   482  gi|130316

     379 HGDGQSYRGTSSTTTTGKKCQSWSSMTPHRHQ-KTPENYPNAGLTMNYCRNPDAD-KGPW   436  gi|130316
          |:|: |||  :|| ||  || |::  ||||   |||  | |||  ||||||| |  |||
     483 FGNGKGYRGKRATTVTGTPCQDWAAQEPHRHSIFTPETNPRAGLEKNYCRNPDGDVGGPW   542  gi|130316

     437 CFTTDPSVRWEYCNLKKCS   455  gi|130316
         |:||:|   ::||:: :|:
     543 CYTTNPRKLYDYCDVPQCA   561  gi|130316

   > 2 gi|130316 len 810 from 102 to 352  vs  gi|130316 len 810 from 274 to 560   score 670
     eval 1.676058e-61 identity 48.00% K 1.978546e-02 L 2.230037e-01 H 1.439763e+00 alpha 1.068759e-01

     102 ECKTGNGKNYRGTMSKTKNGITCQKWSSTSPHRPRFSPATHPSEGLEENYCRNPDNDPQG   161  gi|130316
         :|  | |:|||| :: | :| ||| ||: :||    :|   | : |:||||||||   :
     274 QCLKGTGENYRGNVAVTVSGHTCQHWSAQTPHTHNRTPENFPCKNLDENYCRNPDG-KRA   332  gi|130316

     162 PWCYTTDPEKRYDYCDILECE---------------------EECMHCSGENYDGKISKT   200  gi|130316
         |||:||: : |::|| |  |:                     ::| |  |::| |  | |
     333 PWCHTTNSQVRWEYCKIPSCDSSPVSTEQLAPTAPPELTPVVQDCYHGDGQSYRGTSSTT   392  gi|130316

     201 MSGLECQAWDSQSPHAHGYIPSKFPNKNLKKNYCRNPDRELRPWCFTTDPNKRWELCDIP   260  gi|130316
          :| :||:| | :|| |   |  :||  |  ||||||| :  ||||||||: ||| |::
     393 TTGKKCQSWSSMTPHRHQKTPENYPNAGLTMNYCRNPDADKGPWCFTTDPSVRWEYCNLK   452  gi|130316

     261 RCT-------TPPP-------SSGPTYQCLKGTGENYRGNVAVTVSGHTCQHWSAQTPHT   306  gi|130316
         :|:        |||        :     |: | |: |||  | ||:|  || |:|| ||
     453 KCSGTEASVVAPPPVVLLPDVETPSEEDCMFGNGKGYRGKRATTVTGTPCQDWAAQEPHR   512  gi|130316

     307 HN-RTPENFPCKNLDENYCRNPDGK-RAPWCHTTNSQVRWEYCKIPSC   352  gi|130316
         |:  |||  |   |::||||||||    |||:||| :  ::|| :| |
     513 HSIFTPETNPRAGLEKNYCRNPDGDVGGPWCYTTNPRKLYDYCDVPQC   560  gi|130316

   > 3 gi|130316 len 810 from 100 to 288  vs  gi|130316 len 810 from 374 to 587   score 467
     eval 7.668240e-42 identity 47.34% K 1.978546e-02 L 2.230037e-01 H 1.439763e+00 alpha 1.068759e-01

     100 LSECKTGNGKNYRGTMSKTKNGITCQKWSSTSPHRPRFSPATHPSEGLEENYCRNPDNDP   159  gi|130316
         : :|  |:|::|||| | |  |  || ||| :||| : :|  :|: ||  ||||||| |
     374 VQDCYHGDGQSYRGTSSTTTTGKKCQSWSSMTPHRHQKTPENYPNAGLTMNYCRNPDAD-   432  gi|130316

     160 QGPWCYTTDPEKRYDYCDILEC-----------------------EEECMHCSGENYDGK   196  gi|130316
         :||||:||||  |::||:: :|                       ||:||  :|: | ||
     433 KGPWCFTTDPSVRWEYCNLKKCSGTEASVVAPPPVVLLPDVETPSEEDCMFGNGKGYRGK   492  gi|130316

     197 ISKTMSGLECQAWDSQSPHAHG-YIPSKFPNKNLKKNYCRNPDREL-RPWCFTTDPNKRW   254  gi|130316
          : |::|  || | :| || |  : |   |   |:|||||||| ::  |||:||:| | :
     493 RATTVTGTPCQDWAAQEPHRHSIFTPETNPRAGLEKNYCRNPDGDVGGPWCYTTNPRKLY   552  gi|130316

     255 ELCDIPRCTTPPPSSG-PTYQCLKGTGENYRGNVA   288  gi|130316
         : ||:|:|  |    | |  :  |  |    | ||
     553 DYCDVPQCAAPSFDCGKPQVEPKKCPGRVVGGCVA   587  gi|130316

   > 4 gi|130316 len 810 from 102 to 196  vs  gi|130316 len 810 from 480 to 575   score 284
     eval 4.056174e-24 identity 50.53% K 1.978546e-02 L 2.230037e-01 H 1.439763e+00 alpha 1.068759e-01

     102 ECKTGNGKNYRGTMSKTKNGITCQKWSSTSPHRPR-FSPATHPSEGLEENYCRNPDNDPQ   160  gi|130316
         :|  |||| |||  : |  |  || |::  |||   |:| |:|  |||:||||||| |
     480 DCMFGNGKGYRGKRATTVTGTPCQDWAAQEPHRHSIFTPETNPRAGLEKNYCRNPDGDVG   539  gi|130316

     161 GPWCYTTDPEKRYDYCDILECEEECMHCSGENYDGK   196  gi|130316
         |||||||:| | |||||: :|      |     : |
     540 GPWCYTTNPRKLYDYCDVPQCAAPSFDCGKPQVEPK   575  gi|130316

   pangloss [85]%
Filtering Output

Apart from the built-in threshold -ethresh, ariadne and prospero do not provide any other ways to filter output. However, the perl script prospero.pl will filter output based on alignment length, score, eval and percent identity. Run the script like this:


    prospero -seq1 gi130316.pep | prospero.pl -minscore 600

Use the command-line switches -minscore, -minidentity, -minlen, -maxeval to control the output.
