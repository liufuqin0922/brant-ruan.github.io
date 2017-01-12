<ul>

  {% for post in site.Poem %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

