## DB Deadlines

Countdown timers to keep track of submission deadlines for top **Database, Data Mining, Information Retrieval, Machine Learning and Theory** conferences.

Live at **https://merfanian.github.io/db-deadlines**.

Tracked venues include: VLDB, SIGMOD, PODS, ICDE, EDBT, KDD, ICDM, CIKM, WSDM, SIGIR, WWW, NeurIPS, ICML, ICLR, AAAI, EMNLP, STOC, SODA, and FOCS.

## Contributing

Contributions are very welcome!

To add or update a deadline:
- Fork the repository
- Add/update the relevant file in `_data/conferences/` (one `.yml` file per venue, newest edition first)
- Make sure each entry has the `title`, `year`, `id`, `link`, `deadline`, `timezone`, `date`, `place`, `sub` attributes
    + See available timezone strings [here](https://momentjs.com/timezone/). For "Anywhere on Earth" deadlines use `timezone: UTC-12`.
- Optionally add a `note` and `abstract_deadline` in case the conference has a separate mandatory abstract deadline
- Optionally add `hindex` (h5-index from [Google Scholar](https://scholar.google.com/citations?view_op=top_venues&vq=eng))
- The `sub` tag must be one of: `DB` (Databases), `DM` (Data Mining), `IR` (Information Retrieval), `ML` (Machine Learning), `NLP` (Natural Language Processing), `TH` (Theory)
- Example:
    ```yaml
    - title: BestConf
      year: 2027
      id: bestconf27  # title as lower case + last two digits of year
      full_name: Best Conference for Anything  # full conference name
      link: link-to-website.com
      deadline: '2027-05-25 23:59:00'
      abstract_deadline: '2027-05-18 23:59:00'
      timezone: UTC-12
      place: Incheon, South Korea
      date: September 18-22, 2027
      start: '2027-09-18'
      end: '2027-09-22'
      sub: ['DB']
      note: Important
    ```
- Send a pull request

## Forks & other useful listings

- [geodeadlin.es][3] by @LukasMosser
- [neuro-deadlines][4] by @tbryn
- [ai-challenge-deadlines][5] by @dieg0as
- [CV-oriented ai-deadlines (with an emphasis on medical images)][8] by @duducheng
- [es-deadlines (Embedded Systems, Computer Architecture, and Cyber-physical Systems)][9] by @AlexVonB and @k0nze
- [2019-2020 International Conferences in AI, CV, DM, NLP and Robotics][10] by @JackieTseng
- [ccf-deadlines][11] by @ccfddl
- [networking-deadlines (Computer Networking, Measurement)][12] by @andrewcchu
- [ad-deadlines.com][13] by @daniel-bogdoll
- [sec-deadlines.github.io/ (Security and Privacy)][14] by @clementfung
- [pythondeadlin.es][15] by @jesperdramsch
- [deadlines.openlifescience.ai (Healthcare domain conferences and workshops)][16] by @monk1337
- [hci-deadlines.github.io (Human-Computer Interaction conferences)][17] by @makinteract
- [ds-deadlines.github.io (Distributed Systems, Event-based Systems, Performance, and Software Engineering conferences)][18] by @ds-deadlines
- [https://deadlines.cpusec.org/ (Computer Architecture-Security conferences)][19] by @hoseinyavarzadeh
- [se-deadlines.github.io (Software engineering conferences)][20] by @sivanahamer and @imranur-rahman
- [awesome-mlss (Machine Learning Summer Schools)][21] by @sshkhr and @gmberton

## License

This project is licensed under [MIT][1].

It uses:

- [IcoMoon Icons](https://icomoon.io/#icons-icomoon): [GPL](http://www.gnu.org/licenses/gpl.html) / [CC BY4.0](http://creativecommons.org/licenses/by/4.0/)

[1]: https://abhshkdz.mit-license.org/
[2]: http://aideadlin.es/
[3]: https://github.com/LukasMosser/geo-deadlines
[4]: https://github.com/tbryn/neuro-deadlines
[5]: https://github.com/dieg0as/ai-challenge-deadlines
[6]: http://www.conferenceranks.com/#
[8]: https://m3dv.github.io/ai-deadlines/
[9]: https://ekut-es.github.io/es-deadlines/
[10]: https://jackietseng.github.io/conference_call_for_paper/conferences.html
[11]: https://ccfddl.github.io/
[12]: https://noise-lab.net/networking-deadlines/
[13]: https://ad-deadlines.com/
[14]: https://sec-deadlines.github.io/
[15]: https://pythondeadlin.es/
[16]: https://deadlines.openlifescience.ai/
[17]: https://hci-deadlines.github.io/
[18]: https://ds-deadlines.github.io
[19]: https://deadlines.cpusec.org/
[20]: https://se-deadlines.github.io/
[21]: https://awesome-mlss.com/