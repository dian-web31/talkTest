---Chat GPT options---    

with words as (
    select
        regexp_substr(sentence, '[^ ]+', 1, level) as word
    from
        speech_to_text
    connect by
        level <= regexp_count(sentence, ' ') + 1
        and prior dbms_random.value is not null
        and prior rowid = rowid
)
select word, frequency
from (
    select
        word,
        count(*) as frequency
    from
        words
    group by
        word
    order by
        frequency desc
);