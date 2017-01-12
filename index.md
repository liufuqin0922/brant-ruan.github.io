<ul>

  {% for post in site.categories.Sec %}

    <li>

      <a href="{{ post.url }}">{{ post.date | date_to_string }} &gt;&gt; {{ post.title }}</a>

    </li>

  {% endfor %}

</ul>