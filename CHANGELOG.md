# CHANGELOG

## v2.1.3 (2024-08-08)

### Fix

* fix: pop from extra_typed ([`e18d985`](https://github.com/CRM/mis-project-api/commit/e18d985301e3b2c724af6f51ca50b522b5c5c901))

* fix: offers and lands ids only str ([`865f747`](https://github.com/CRM/mis-project-api/commit/865f747245e2fd6199b19f406f5a8704e5b97971))

### Unknown

* Merge pull request &#39;MIS-134+195&#39; (#97) from MIS-134+195 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/97
Reviewed-by: jake.jameson &lt;jake.jameson9983@gmail.com&gt; ([`13f6a88`](https://github.com/CRM/mis-project-api/commit/13f6a8804fb33ab27b2cd8fba1d698d2e7af5f56))

* renamed migration ([`d43f9fb`](https://github.com/CRM/mis-project-api/commit/d43f9fbb79c3b39d85808196c25e40ae01185100))

* renamed client_data to user_data; edit_user_data removed scopes ([`adaf614`](https://github.com/CRM/mis-project-api/commit/adaf614ba92ba5513ba43227d11389edf4f62f5a))

* client_data and admin user update restrictions ([`997994b`](https://github.com/CRM/mis-project-api/commit/997994b73962208c94c34d21a2352ec56ac7ae99))

* Merge pull request &#39;MIS-192+218&#39; (#96) from MIS-192+218 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/96 ([`24bcf32`](https://github.com/CRM/mis-project-api/commit/24bcf32b7de5a40ce6b8b16b4b82418fb3d2504e))

* remove context_logger ([`14d796e`](https://github.com/CRM/mis-project-api/commit/14d796e6f0809cfe0418701f70132b50acb820ce))

* mongo for JobExecutionStorage ([`4a368fa`](https://github.com/CRM/mis-project-api/commit/4a368fa94230e08d3acb953c08335d938d3d1df8))

* removed logger from job arguments, using with logger.contextualize instead ([`1713ddf`](https://github.com/CRM/mis-project-api/commit/1713ddf88d10505d3f4116aabece7c0912d24187))

* job logs and execute history ([`52dfc87`](https://github.com/CRM/mis-project-api/commit/52dfc8784a1410fb82ace65aa9cceb83eefd959b))

* Merge pull request &#39;binom companion hotfix&#39; (#95) from binom-companion-fix into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/95 ([`716bda2`](https://github.com/CRM/mis-project-api/commit/716bda2e15d59f838262351b4601687dc7845c0c))

* added proper migration ([`8ffeaff`](https://github.com/CRM/mis-project-api/commit/8ffeaff93209c7e426257b5c6e3f1da8d4d24cab))

* fix bulk creating and dns checker ([`8f356e6`](https://github.com/CRM/mis-project-api/commit/8f356e6f519d5fc5c2296582a465bbdac28eb0c5))

* Merge pull request &#39;ITG-850-UPDATE&#39; (#94) from ITG-850-update into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/94 ([`a2e1b5b`](https://github.com/CRM/mis-project-api/commit/a2e1b5b0439997ebd48bf31f69131459abb0bba2))

* new endpoint check_domains ([`256f6f0`](https://github.com/CRM/mis-project-api/commit/256f6f0e6a3b86e6034f1acb3ecf58f982a991d2))

* Merge pull request &#39;ITG-849-UPDATE&#39; (#93) from ITG-849-update into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/93 ([`17f32e9`](https://github.com/CRM/mis-project-api/commit/17f32e9668f92d5cb1f9d36c4b4ff692fc7d12a6))

* fix landings_list ([`5e0a0af`](https://github.com/CRM/mis-project-api/commit/5e0a0af6c0e254cb8a3d336880ee525b10ba7150))

* reduced get keitaro requests when change domains; run update requests in asyncio.gather ([`ca2be26`](https://github.com/CRM/mis-project-api/commit/ca2be2651cc23c940806ac38b27bd566e0fa66c6))

* Merge pull request &#39;fix tests&#39; (#92) from fix-tests into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/92 ([`d9ca08d`](https://github.com/CRM/mis-project-api/commit/d9ca08d5cbca56c195e9d48034b8bc132ea7e456))

* changelog for fix tests ([`ae8f3de`](https://github.com/CRM/mis-project-api/commit/ae8f3de116162f9ceb103565d3d47c1dcf343030))

* fix tests ([`9eb7c2a`](https://github.com/CRM/mis-project-api/commit/9eb7c2a6b60ed9ae905ca1373087a81b742ffad2))

* Merge pull request &#39;ITG-853-fix-3&#39; (#91) from fix_history_pydantic_model into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/91 ([`ea252e2`](https://github.com/CRM/mis-project-api/commit/ea252e2146b0874e2db94c6042df41bb023c3e9e))

* changed typing offers and lands to list[str | int] ([`7e448f8`](https://github.com/CRM/mis-project-api/commit/7e448f8216209084ed24468d3b2a5b7fe07befa1))

* Merge pull request &#39;ITG-853-fix-2&#39; (#90) from ITG-853-fix into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/90 ([`0872fea`](https://github.com/CRM/mis-project-api/commit/0872feaffce62daa0ad98779b20afd361707805e))

* remove cursor ([`1c086a2`](https://github.com/CRM/mis-project-api/commit/1c086a21257573e69302b8a63813e375e5e4b035))

* Merge pull request &#39;ITG-853-fix&#39; (#89) from ITG-853-fix into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/89 ([`8a36dde`](https://github.com/CRM/mis-project-api/commit/8a36dde0a1a8ad6c5deb37a88d91cc393c56f968))

* fixed transferring proxy domain with trackers to new table ([`2fe68d4`](https://github.com/CRM/mis-project-api/commit/2fe68d4df8defe11032c769787fa27781b45e947))

## v2.1.2 (2024-07-22)

### Fix

* fix: changed match to search ([`228a797`](https://github.com/CRM/mis-project-api/commit/228a79780d2b553f5908f5115fb4686ffc13dad8))

### Unknown

* Merge pull request &#39;ITG-853&#39; (#88) from ITG-853 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/88 ([`33d70ab`](https://github.com/CRM/mis-project-api/commit/33d70ab066825a78ce4835989bab3939e03e1259))

* version update to v2.1.2 ([`0b385b0`](https://github.com/CRM/mis-project-api/commit/0b385b0baf4b5fcb5f1385493393182baff3241f))

* changelog ITG-853 moved to v2.1.2 ([`dd00231`](https://github.com/CRM/mis-project-api/commit/dd00231e6dec3448aa300bc6a4f23499e02a3fb3))

* update transferring for all TrackerInstance ([`c8570af`](https://github.com/CRM/mis-project-api/commit/c8570af66c25c63fdb376efd32759166fabb1e20))

* added transferring data to new table in migration ([`5562f64`](https://github.com/CRM/mis-project-api/commit/5562f642930511da1331b5761cd0f74206e4e0c8))

* changed tracker_instance in ProxyDomain to multiple tracker_instances (m2m) ([`476e54c`](https://github.com/CRM/mis-project-api/commit/476e54c2a358d3ce6d4aaa217b7559890b356c81))

* Merge pull request &#39;HOTFIX ITG-850&#39; (#87) from fix_regexp_match into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/87 ([`53a547a`](https://github.com/CRM/mis-project-api/commit/53a547a2df2dfbf339d4e353c62b51bbea13bc10))

* Merge pull request &#39;HOTFIX ITG-850&#39; (#86) from fix_field_name into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/86 ([`d5d0a38`](https://github.com/CRM/mis-project-api/commit/d5d0a3850d4bb540963cca4a7fc3d01c16c0bc45))

* fix field name ([`3ef45bf`](https://github.com/CRM/mis-project-api/commit/3ef45bf1922cc9c6e642012d211a2c032c570ef2))

* version update ([`07a0aca`](https://github.com/CRM/mis-project-api/commit/07a0aca18eeab0e8e8f150237bc580a8a8a4d59b))

* Merge pull request &#39;ITG-850&#39; (#85) from ITG-850 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/85 ([`9609018`](https://github.com/CRM/mis-project-api/commit/96090185aa00d9cf58eec6ed45d724ed359bbf9e))

* domains checks ([`459f2bb`](https://github.com/CRM/mis-project-api/commit/459f2bb1699f7861756e3b3825eda853114d6c8d))

## v2.1.1 (2024-07-17)

### Unknown

* Merge pull request &#39;ITG-849&#39; (#84) from ITG-849 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/84
Reviewed-by: jake.jameson &lt;jake.jameson9983@gmail.com&gt; ([`b7cd59f`](https://github.com/CRM/mis-project-api/commit/b7cd59f17593ad01dc66191557b7c5b0b1d42aaa))

* renamed type to tracker_type ([`9d01a64`](https://github.com/CRM/mis-project-api/commit/9d01a64c06a6651120d5ca3151d2a44df0c5127c))

* added filters by name_regexp_pattern and offer_geo ([`9a156ea`](https://github.com/CRM/mis-project-api/commit/9a156ea1d9948a0d7f3865eed59282ae7b036aaa))

* domain changing for keitaro ([`ed7fc66`](https://github.com/CRM/mis-project-api/commit/ed7fc66eb638abf0f6831216ba7566c020f68412))

* Update requirements.txt ([`427a4ac`](https://github.com/CRM/mis-project-api/commit/427a4accf84d7d5048f52fa8f15dde28e9be23ee))

## v2.1.0 (2024-06-17)

### Unknown

* upd versions and docs ([`1f790a3`](https://github.com/CRM/mis-project-api/commit/1f790a332217a7f1a7e87adeac6ef86e9d6ce38c))

* partially fixed dataset ([`002b585`](https://github.com/CRM/mis-project-api/commit/002b58557bad08165a42d95451724a2f0e9f9ec3))

* Merge pull request &#39;MIS-89, MIS-219&#39; (#83) from MIS-219 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/83 ([`ab03f41`](https://github.com/CRM/mis-project-api/commit/ab03f416b77e1e4d05fcb0a7b83df75dd75ed144))

* global vars now in VariableValue model; using pydantic TypeAdapter for validate input variable value ([`20fda9c`](https://github.com/CRM/mis-project-api/commit/20fda9cf8de2075b7b788cb887e75b8b285faa4b))

* changelog ([`82fe13f`](https://github.com/CRM/mis-project-api/commit/82fe13f5ad3491ad9c188ad673443aa1acaf8152))

* log manager and callbacks when variables changing ([`46e77f5`](https://github.com/CRM/mis-project-api/commit/46e77f54f6cb01ede73af40a32a7a8c07700ebc9))

* Merge pull request &#39;MIS-184&#39; (#82) from MIS-184 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/82 ([`4d71abd`](https://github.com/CRM/mis-project-api/commit/4d71abdd29940e278bb3027d21e73c78abc8f356))

* fixed dummy init with guardian example ([`6013212`](https://github.com/CRM/mis-project-api/commit/60132126366fd17333c77769ba65ad7ccca6a442))

* Merge pull request &#39;MIS-194: fix for trigger&#39; (#81) from MIS-194 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/81 ([`8fb331a`](https://github.com/CRM/mis-project-api/commit/8fb331a4cf16d5953ba04c34f59f576680dfb169))

* fix for trigger ([`8ded96b`](https://github.com/CRM/mis-project-api/commit/8ded96b164f5f94a6536a3589854b3153f9f532d))

* Merge pull request &#39;MIS-197&#39; (#80) from MIS-197 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/80 ([`4027e4d`](https://github.com/CRM/mis-project-api/commit/4027e4d64163becfc34f270b49843b9f91a9aebe))

* update ([`9d907e0`](https://github.com/CRM/mis-project-api/commit/9d907e0aa243cbe4c75208b0a74beced06c47d95))

* Merge pull request &#39;MIS-194&#39; (#79) from MIS-194 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/79 ([`0f8bdeb`](https://github.com/CRM/mis-project-api/commit/0f8bdebe9c1fdc295314b44eb7937595031dd2d6))

* update ([`d126d3e`](https://github.com/CRM/mis-project-api/commit/d126d3e37947343c5102af519bfd40359dd5c6fb))

* Update dns_checker.py ([`270303d`](https://github.com/CRM/mis-project-api/commit/270303d6b52da4d3045cadb7bd14bedf371590fa))

* Merge branch &#39;v2.0.5&#39; ([`8fb241c`](https://github.com/CRM/mis-project-api/commit/8fb241c64c27d2262d9d96f57c1d3cadfeb8f884))

* fix imports ([`9a48a23`](https://github.com/CRM/mis-project-api/commit/9a48a23ce05bc73c8c2021a8659a59d7934a8ff2))

* Merge branch &#39;v2.0.5&#39; ([`86e3fce`](https://github.com/CRM/mis-project-api/commit/86e3fce2197ea8aaa2adfeccfd4e520522a0b920))

* unplanned fixes and changes ([`bf5ef1d`](https://github.com/CRM/mis-project-api/commit/bf5ef1da2bce8f27c5a694e9dfc4bbd7d6020afc))

* Merge pull request &#39;MIS-208 unplanned changes&#39; (#77) from MIS-208 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/77 ([`5a3867b`](https://github.com/CRM/mis-project-api/commit/5a3867b1e8ef4a7c340f190db9d0cca4a42f2540))

* upd fix ([`ef8cbc3`](https://github.com/CRM/mis-project-api/commit/ef8cbc33d699c4f567c85168067823a3954ef93d))

* shit merge resolved ([`54c80f8`](https://github.com/CRM/mis-project-api/commit/54c80f853cf3eb369569ab0c1b0c348569eb58d8))

* Merge pull request &#39;upd&#39; (#75) from MIS-193 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/75 ([`e6ca2a4`](https://github.com/CRM/mis-project-api/commit/e6ca2a4e979ff166119ec545fb6ed6b03efa19c8))

* upd ([`5d48bbe`](https://github.com/CRM/mis-project-api/commit/5d48bbe4f279b89acbbd74ab1e551b19804d6815))

* Create CI-CD.md ([`03454cd`](https://github.com/CRM/mis-project-api/commit/03454cd8b615df186444ce10a56426f765d7de2a))

* Merge pull request &#39;MIS-205&#39; (#74) from MIS-205 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/74 ([`5c30e26`](https://github.com/CRM/mis-project-api/commit/5c30e262855f3ccada6a2786f9e067c0d3aa5e9b))

* upd ([`9e22565`](https://github.com/CRM/mis-project-api/commit/9e22565df6a3bd794c223ab68a47e2a01eb3ea42))

* Merge pull request &#39;MIS-208&#39; (#73) from MIS-208 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/73 ([`377538f`](https://github.com/CRM/mis-project-api/commit/377538f973972f1fa5320cae279840523f457562))

* Create MIS-208.md ([`3bc30be`](https://github.com/CRM/mis-project-api/commit/3bc30bec0fc9f7c31ae987399dbc7095790b9150))

* resolved conflict ([`eb88d4f`](https://github.com/CRM/mis-project-api/commit/eb88d4f2e8010c7553e1f216c4fe9a3f61ebc741))

* Merge branch &#39;main&#39; into MIS-208 ([`0048182`](https://github.com/CRM/mis-project-api/commit/0048182e8bcb0fbe4f2aeef5437978185bdda26c))

* Merge pull request &#39;MIS-189&#39; (#72) from MIS-189 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/72 ([`dfdc1c7`](https://github.com/CRM/mis-project-api/commit/dfdc1c77db53e5525d3df50a2f05e39c7208b83d))

* changelog MIS-189 ([`9f3a4ec`](https://github.com/CRM/mis-project-api/commit/9f3a4ec2ba2a97a5e921dba71b8c521eef6b837c))

* removed EventoryService; moved make_routing_keys_set to RoutingKeyService ([`229f2a9`](https://github.com/CRM/mis-project-api/commit/229f2a9e71094f14847c64fb8e88b5fd4968c596))

* fix validated_body typing ([`77ae922`](https://github.com/CRM/mis-project-api/commit/77ae922787c14208a48b00b34add834ea2228597))

* pydantic validation for consumers ([`036f1e9`](https://github.com/CRM/mis-project-api/commit/036f1e92e985b9e6c0f6d570acc48e9426104d07))

* refactoring eventory ([`103decc`](https://github.com/CRM/mis-project-api/commit/103decc89a9e8319b0a5bb0f4d5041f1c89af3bc))

* fixes ([`349df97`](https://github.com/CRM/mis-project-api/commit/349df97f16d3ea88cafcd6b757306090684ee795))

* refactor ([`095040e`](https://github.com/CRM/mis-project-api/commit/095040e051e16d6c33e9f1b1bf48c2e1a531891c))

* refactor ([`0e0d925`](https://github.com/CRM/mis-project-api/commit/0e0d925a7f2960cb16eda8586d4ffb405450ca29))

* refactoring ([`1ee9e76`](https://github.com/CRM/mis-project-api/commit/1ee9e7661e1694d6a68215663a1afc555eb7e722))

* import fixes ([`ee210f3`](https://github.com/CRM/mis-project-api/commit/ee210f3ddda27b70a07b13222322aebc8ebc701b))

* modules rewrite wip ([`51466a8`](https://github.com/CRM/mis-project-api/commit/51466a81b59d57e0b57380f468d734ca8a75c33c))

* modules rework WIP ([`b19cba7`](https://github.com/CRM/mis-project-api/commit/b19cba7d26e4b299537d49fcebd47baa536ec3fb))

* scheduler update ([`30688b4`](https://github.com/CRM/mis-project-api/commit/30688b42bce4d4db95e0a810b0adaf53afd0d041))

* upd ([`d77ebb4`](https://github.com/CRM/mis-project-api/commit/d77ebb450c68ddb69e7f204de004243db58d6fd9))

* upd ([`54354a6`](https://github.com/CRM/mis-project-api/commit/54354a6cd8eb05fdeb40289b8d92fe3255f67381))

* Merge pull request &#39;MIS-202&#39; (#71) from MIS-202 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/71 ([`7573a17`](https://github.com/CRM/mis-project-api/commit/7573a1756f6c399a5f5fa18247b554febd2f5a0c))

* upd ([`779451b`](https://github.com/CRM/mis-project-api/commit/779451bb92f824aee146ad6ed8ef966827f8cf94))

* upd ([`3835a41`](https://github.com/CRM/mis-project-api/commit/3835a412c5a7a4c7f877fe7dd142fdd30a55a280))

* Update main.py ([`bc94903`](https://github.com/CRM/mis-project-api/commit/bc9490399f60fcd4acd1dc04b2e0a1b204e475ce))

* upd ([`47b3535`](https://github.com/CRM/mis-project-api/commit/47b3535e4900d7cec81e07f938934898a7a28814))

* Merge pull request &#39;MIS-188&#39; (#70) from MIS-188 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/70 ([`a2d5431`](https://github.com/CRM/mis-project-api/commit/a2d5431bafc6882e0cf9d7d71d112c4edef3d72b))

* Create MIS-188.md ([`6fe7adf`](https://github.com/CRM/mis-project-api/commit/6fe7adf1dc678c1a8dca18a913d9d3ac79bff242))

* permission fixed and scopes added ([`05e2dd2`](https://github.com/CRM/mis-project-api/commit/05e2dd264c15a9b83ebd2b1f88c1750b58cc4854))

* upd docs ([`ebb2153`](https://github.com/CRM/mis-project-api/commit/ebb21539efadbac37153e12adfb8d09fb3978a67))

* Merge pull request &#39;v2.0.5&#39; (#69) from v2.0.5 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/69 ([`1c3cbcd`](https://github.com/CRM/mis-project-api/commit/1c3cbcd9f77facffdc97b65f138b479fb6304f4f))

* Update v2.0.5.md ([`7c488fc`](https://github.com/CRM/mis-project-api/commit/7c488fc70bd3ef8b393ab29e730dee6444a9f344))

* update ([`edd501b`](https://github.com/CRM/mis-project-api/commit/edd501bc1ef8454f6e648f1c272fd6b65554f8b7))

* Merge pull request &#39;update&#39; (#68) from v2.0.5 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/68 ([`ee36e89`](https://github.com/CRM/mis-project-api/commit/ee36e890a02eb5fed2701fcbe20b0e9c3e4f8529))

* update ([`4675522`](https://github.com/CRM/mis-project-api/commit/46755226f8f09da1fa444b7f8f600337aedc4519))

## v2.0.4 (2024-06-03)

### Unknown

* Merge pull request &#39;2.0.4&#39; (#67) from 2.0.4 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/67 ([`7e7a6c7`](https://github.com/CRM/mis-project-api/commit/7e7a6c78e3e35c8487083d80f27e57482d42f392))

* added changelog ([`c9ef26f`](https://github.com/CRM/mis-project-api/commit/c9ef26fb7e892466a9ef785e4ea2707ab1c039bb))

* multiple fixes ([`23830e4`](https://github.com/CRM/mis-project-api/commit/23830e4b35b87a13631526cad2f7d0d470467494))

* Merge branch &#39;main&#39; of glum.nianmasters.net:CRM/mis-project-api ([`ce95e2e`](https://github.com/CRM/mis-project-api/commit/ce95e2e5ebaf8794225550836a30cabb14476cf0))

## v2.0.3 (2024-05-31)

### Unknown

* Merge pull request &#39;update&#39; (#66) from v2.0.3 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/66 ([`3a6d37f`](https://github.com/CRM/mis-project-api/commit/3a6d37f4f85b5d4e187e19e58256cd4d2ba4e2d5))

* update ([`80bbadf`](https://github.com/CRM/mis-project-api/commit/80bbadf79e73a5c22bfc72f8aa1ba0ec873465ce))

* todo cleanup and converted to tasks ([`33358e0`](https://github.com/CRM/mis-project-api/commit/33358e07d695a76c9336dbaa8d9d26fb9cebf771))

* Merge pull request &#39;changelog for core 2.0.0; docs for guardian and repositories with services&#39; (#65) from changelog_and_docs into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/65 ([`536296f`](https://github.com/CRM/mis-project-api/commit/536296f6e75d4dd8f66a3c1615426f0ac19cf18c))

* changelog for core 2.0.0; docs for guardian and repositories with services ([`c7e2717`](https://github.com/CRM/mis-project-api/commit/c7e2717c8877d9f1cb21fdf9231eb33ddd995170))

## v2.0.2 (2024-05-30)

### Unknown

* Merge pull request &#39;update&#39; (#64) from v2.0.2 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/64 ([`cde30fe`](https://github.com/CRM/mis-project-api/commit/cde30fe983cdc0a9b3a1d63326e0ea2f29af1ded))

* update ([`a6d83e6`](https://github.com/CRM/mis-project-api/commit/a6d83e6a387e055a346a4206108e5dfd6d737d94))

## v2.0.1 (2024-05-30)

### Unknown

* Merge pull request &#39;v2.0.1&#39; (#63) from v2.0.1 into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/63 ([`bc4a985`](https://github.com/CRM/mis-project-api/commit/bc4a9857267027669bf6d65889893595af965aba))

* removed trash ([`d05703a`](https://github.com/CRM/mis-project-api/commit/d05703ad48303187878ca0d4835dee9989681744))

* miltiple updates ([`4be724e`](https://github.com/CRM/mis-project-api/commit/4be724ef514e880d058fe6fa43aa8f910c53a0aa))

* Merge pull request &#39;added env ALLOW_ORIGINS to settings&#39; (#62) from origins_from_env into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/62 ([`d68c4d7`](https://github.com/CRM/mis-project-api/commit/d68c4d7ca1eb3db650a4f5ddf2445f069d8c6bfa))

* added env ALLOW_ORIGINS to settings ([`e042bf2`](https://github.com/CRM/mis-project-api/commit/e042bf24889b92db5d4d122e0e5a98f1dd66af71))

* Merge pull request &#39;fixed migrations&#39; (#61) from fix_migrations into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api/pulls/61 ([`c979595`](https://github.com/CRM/mis-project-api/commit/c979595f5ad323153ddcfcc1f0c5f71c4c3925e7))

* fixed migrations ([`d89419a`](https://github.com/CRM/mis-project-api/commit/d89419a7e67ffdf9dc984e34f8101fbd819ada34))

## v2.0.0 (2024-05-28)

### Unknown

* Update .gitignore ([`dc244d3`](https://github.com/CRM/mis-project-api/commit/dc244d36fc13e09c27ff3a5139deab3f111b5776))

* Update pre v2 - v2.0.0.md ([`e876376`](https://github.com/CRM/mis-project-api/commit/e8763763580ea5f386d77a973c1581e3fe8114a3))

* Update pre v2 - v2.0.0.md ([`198d045`](https://github.com/CRM/mis-project-api/commit/198d0455d75e4e02d53c60df1f44de678fc8915f))

* doc upd ([`c91c041`](https://github.com/CRM/mis-project-api/commit/c91c041ab4fa2cb8db1e8542d5f28262c9bfd6e5))

* docs init, increased versions ([`fc2c02f`](https://github.com/CRM/mis-project-api/commit/fc2c02ff6ec6ff99b2e15dc7077d5f61d177d158))

* Merge pull request &#39;binom_companion&#39; (#36) from binom_companion into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/36 ([`39fc87f`](https://github.com/CRM/mis-project-api/commit/39fc87f65ae1634681f113df5b28d85cfd8cedbb))

* check for remove sudo perm to admin user ([`f135bb6`](https://github.com/CRM/mis-project-api/commit/f135bb6cc21714a3bb80a40d4f76ec993b42c881))

* Merge branch &#39;main&#39; into binom_companion ([`b14be71`](https://github.com/CRM/mis-project-api/commit/b14be71f7d8aee4e2a8827ba9b9f3023d9ed365f))

* Merge pull request &#39;removed transactions for set_paused_status and set_running_status; removed updated_obj.save(), save is used in repo&#39; (#35) from resume_job_without_transaction into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/35 ([`5163393`](https://github.com/CRM/mis-project-api/commit/5163393d1467b646badcdff756a3b229f812c05a))

* additional checks for sync db jobs and scheduler jobs ([`2a94c49`](https://github.com/CRM/mis-project-api/commit/2a94c492247016d79ddd38480d299bf9a117ef49))

* removed transactions for set_paused_status and set_running_status; removed updated_obj.save(), save is used in repo ([`256fff0`](https://github.com/CRM/mis-project-api/commit/256fff03d8d69e37206376ff4890dc086dcdcd22))

* fixed migrations typo, added permission migration, permikssions fix for bc ([`d214011`](https://github.com/CRM/mis-project-api/commit/d214011e7ba0d851f1b1234834e520f8aeffe7bd))

* fix type instead of instance ([`17c56cd`](https://github.com/CRM/mis-project-api/commit/17c56cd9115a3da944c4c84c7a4001eda122bee9))

* Merge pull request &#39;replaced in_transaction context manager to atomic decorator&#39; (#34) from replace_transactions into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/34 ([`fc49187`](https://github.com/CRM/mis-project-api/commit/fc491877aefb0c8523f7b0310878bef552bab94c))

* replaced in_transaction context manager to atomic decorator ([`ae7c573`](https://github.com/CRM/mis-project-api/commit/ae7c573246b55412625cf0964a20bcd60545f61e))

* Merge pull request &#39;binom_companion&#39; (#33) from binom_companion into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/33 ([`20c6540`](https://github.com/CRM/mis-project-api/commit/20c654017fa53ac4ea0099b72a15996aa355f650))

* apply migrations little improvements ([`a2492c8`](https://github.com/CRM/mis-project-api/commit/a2492c806422aea25638890b80c9501d3e247e3f))

* cleanup ([`9a36373`](https://github.com/CRM/mis-project-api/commit/9a363738d53018c7fcc894474c409a9d1daab529))

* Merge branch &#39;main&#39; into binom_companion ([`8140136`](https://github.com/CRM/mis-project-api/commit/8140136f6cc1c7ecd8203a125a7ed5c3fa0bb24b))

* Merge pull request &#39;fixed limit replacement history; added history order by date_changed&#39; (#31) from limit_history into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/31 ([`ba7a6db`](https://github.com/CRM/mis-project-api/commit/ba7a6dbc2ff0ed2e428a9a048c74575db5784651))

* Merge branch &#39;main&#39; into limit_history ([`9879aac`](https://github.com/CRM/mis-project-api/commit/9879aac13054615cb7916eb72a085e50d0a2786a))

* Merge pull request &#39;routing_key_to_dict moved to RoutingKeyService&#39; (#32) from fix_circular_import into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/32 ([`418fddc`](https://github.com/CRM/mis-project-api/commit/418fddc640a0a253e8da740555df23bca8f8fc0f))

* routing_key_to_dict moved to RoutingKeyService ([`139c996`](https://github.com/CRM/mis-project-api/commit/139c996fba08e8a04dc8148db2d31c223876ad4f))

* fixed limit replacement history; added history order by date_changed ([`990bde1`](https://github.com/CRM/mis-project-api/commit/990bde103267e933c93808adafdaa6f288bf9609))

* Merge pull request &#39;example for nested prefetch and custom Prefetch; added bulk update in base repo and service&#39; (#29) from dummy_example_prefetch into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/29 ([`fdba329`](https://github.com/CRM/mis-project-api/commit/fdba32951e2ba84ef532c6e92a0e0c21bce83128))

* exemple for update_list method ([`57f62d7`](https://github.com/CRM/mis-project-api/commit/57f62d75a0eb0208e2977ccc91ca6e45ef2bbebd))

* example for nested prefetch and custom Prefetch; added bulk update in base repo and service ([`19cf98c`](https://github.com/CRM/mis-project-api/commit/19cf98c8a402855adad516325ea56cc467d2aeac))

* Merge pull request &#39;redis logic moved to service; fixed response_model for subscribe; fixed unsubscribe&#39; (#30) from notification_fix into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/30 ([`f9c718f`](https://github.com/CRM/mis-project-api/commit/f9c718f554a970699eb03de48ef4ab06e7c5ce97))

* redis logic moved to service; fixed response_model for subscribe; fixed unsubscribe ([`9bc61c0`](https://github.com/CRM/mis-project-api/commit/9bc61c0bba326ce7e8a365fb261b7c1456df04c2))

* wip ([`a2efa7c`](https://github.com/CRM/mis-project-api/commit/a2efa7c29081354173668b6d0fb5292e5a201497))

* Update repository.py ([`06b3004`](https://github.com/CRM/mis-project-api/commit/06b30043c501d8198ddb35e3662b3900c0814b6e))

* Merge branch &#39;main&#39; into binom_companion ([`1378154`](https://github.com/CRM/mis-project-api/commit/1378154eabc7b9c4585f68e00e007a41523c32f6))

* Merge pull request &#39;more usage examples for dummy module; mongodb, redis, websockets, dependencies&#39; (#28) from dummy_examples into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/28 ([`69a0824`](https://github.com/CRM/mis-project-api/commit/69a082498deb45a24a727762c94353d867a920f9))

* more usage examples for dummy module; mongodb, redis, websockets, dependencies ([`2933467`](https://github.com/CRM/mis-project-api/commit/293346760a583bfcc881c325df00afaf3cbf043c))

* Merge pull request &#39;new_task_check_dns_record&#39; (#27) from new_task_check_dns_record into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/27 ([`066d6e9`](https://github.com/CRM/mis-project-api/commit/066d6e9c984c8e607a619aea22200638a0865e4d))

* added aiodns dependency ([`042853f`](https://github.com/CRM/mis-project-api/commit/042853f4b158772af816c5803934e6b3d3ebe6a9))

* binom_companion: new task proxy_domains_dns_record_checker ([`b76e0b7`](https://github.com/CRM/mis-project-api/commit/b76e0b786dcdff48a38cb8943851d99b7441e0bb))

* Merge pull request &#39;limit ReplacementHistory in ReplacementGroup&#39; (#26) from replacement_history_limit into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/26 ([`040053c`](https://github.com/CRM/mis-project-api/commit/040053c4c26223acd4c7c74b4276dc8894bd6311))

* limit ReplacementHistory in ReplacementGroup ([`894a18c`](https://github.com/CRM/mis-project-api/commit/894a18ce0b2df4d0b3603338eda60924bf899f7a))

* Merge pull request &#39;binom_companion: new task domain_ban_monitor and extend scheduled_tasks&#39; (#25) from task_domain_ban_monitor into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/25 ([`f47ecca`](https://github.com/CRM/mis-project-api/commit/f47ecca43bca98acb461a4385f2015c1043bde14))

* binom_companion: new task domain_ban_monitor and extend scheduled_tasks ([`2538fd9`](https://github.com/CRM/mis-project-api/commit/2538fd9b39b9107e7777bdcf9c843d84b12bd37d))

* Merge pull request &#39;fixes&#39; (#24) from fixes into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/24 ([`bff458d`](https://github.com/CRM/mis-project-api/commit/bff458d677d6866d7993edeb24fe58fbfffa618b))

* dependencies for proxy_registry module ([`0588ef0`](https://github.com/CRM/mis-project-api/commit/0588ef05eb80c41839f30b3e4b605d03b4a4298b))

* fixed saving object after update_from_dict ([`863f505`](https://github.com/CRM/mis-project-api/commit/863f505cbd28d1c1c06dcf1913a0ee0649d8177f))

* fixed tests ([`64ee21c`](https://github.com/CRM/mis-project-api/commit/64ee21caf303ed1367bb9ca54c0a4a277f7b72f3))

* added filter by module_name for get modules and variables ([`3ca86d3`](https://github.com/CRM/mis-project-api/commit/3ca86d307ecb8eedbee2ef7911049f89247c0efd))

* Merge pull request &#39;fixed job restore issue, binom companion improvements&#39; (#23) from binom_companion into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/23 ([`04d09f6`](https://github.com/CRM/mis-project-api/commit/04d09f619577f6b89aa8aad172effc36c2225021))

* Merge pull request &#39;added module proxy_registry&#39; (#22) from proxy_registry into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/22 ([`b3ed766`](https://github.com/CRM/mis-project-api/commit/b3ed76673530f224dc09fb0388f02125548f1fb2))

* added module proxy_registry ([`ac3b1da`](https://github.com/CRM/mis-project-api/commit/ac3b1da2c14f7892be518931f403faffe8d49eef))

* removed deprecated and bc improvements (broken) ([`e2eb80c`](https://github.com/CRM/mis-project-api/commit/e2eb80c38dfc7095acd01ddeba9c4f42716244d0))

* fixed job restore issue, binom companion improvements ([`8accb9f`](https://github.com/CRM/mis-project-api/commit/8accb9f2f211fc09fac284a524c3bf22629539cb))

* Merge pull request &#39;modules_reintroduce_with_removed_uow&#39; (#20) from modules_reintroduce_with_removed_uow into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/20 ([`e706ccb`](https://github.com/CRM/mis-project-api/commit/e706ccb219116b5cfc8cf5e3237a3110674afbcf))

* port 8000; raise AlreadyExists ([`23781f7`](https://github.com/CRM/mis-project-api/commit/23781f7de28a6a7788f5e419a0c8c43e33a7ad8d))

* Merge branch &#39;main&#39; into modules_reintroduce_with_removed_uow ([`64c43b3`](https://github.com/CRM/mis-project-api/commit/64c43b31f6ab53150083c1d22a6fdc1246ebcb57))

* Merge pull request &#39;modules_reintroduce&#39; (#21) from modules_reintroduce into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/21 ([`1a710cb`](https://github.com/CRM/mis-project-api/commit/1a710cbe00bdfeb573fd37238b6a943b03209bd3))

* fix merge ([`b3b1da5`](https://github.com/CRM/mis-project-api/commit/b3b1da5fd6faef65ee6ab00b6007de9d77e26b29))

* Merge branch &#39;remove_uow&#39; into modules_reintroduce_with_removed_uow ([`da9e6c7`](https://github.com/CRM/mis-project-api/commit/da9e6c74bab296ca3bce3466fa39db76875594fc))

* removed unit of work layer ([`7f35791`](https://github.com/CRM/mis-project-api/commit/7f3579191955b0565ee487628bd39e58a8cb39e4))

* added init migrations ([`e8db66e`](https://github.com/CRM/mis-project-api/commit/e8db66ec6e96c622b279ebd1dddc9c79c2714947))

* fixes, cleanups and test passed ([`7123bd1`](https://github.com/CRM/mis-project-api/commit/7123bd1475b3d2165e6214bdc37412a94b4a636f))

* binom companion reworked ([`ca53fd5`](https://github.com/CRM/mis-project-api/commit/ca53fd5ad419d51986ce53296256bfbe195ae236))

* WIP massive pack of changes ([`af8169d`](https://github.com/CRM/mis-project-api/commit/af8169dea0a3a767237c6906482d00707efa1771))

* Merge pull request &#39;wip-changes&#39; (#19) from wip-changes into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/19 ([`53c65f2`](https://github.com/CRM/mis-project-api/commit/53c65f2f8b7ceed877d87e960705922d1ec5961e))

* fixes after merge ([`08e434b`](https://github.com/CRM/mis-project-api/commit/08e434b9adeb23ca8773954c467abafb6ef03c34))

* Merge branch &#39;main&#39; into wip-changes ([`f330dfe`](https://github.com/CRM/mis-project-api/commit/f330dfeab923fb9036a90851fd80864542c5f94f))

* Merge pull request &#39;remove-crud&#39; (#18) from remove-crud into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/18 ([`58af9be`](https://github.com/CRM/mis-project-api/commit/58af9beaa7a8d02176ce1da643903899e6d72cbf))

* rewritten guardian logic to repository+service ([`416e6a4`](https://github.com/CRM/mis-project-api/commit/416e6a4a41aaa34cc4fcbec87c73a662130432c6))

* removed crud, replaced by repository+service ([`3a643f7`](https://github.com/CRM/mis-project-api/commit/3a643f79950905649a2a7edf1eb8971cabdf0a2a))

* wip changes ([`9f87209`](https://github.com/CRM/mis-project-api/commit/9f87209dec945d9926f4a23f9277316400b3f197))

* Merge pull request &#39;guardian mixin&#39; (#17) from guardian_mixin into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/17 ([`a9798c2`](https://github.com/CRM/mis-project-api/commit/a9798c23b215f28b8906fba4f7ebc55f43dc2d08))

* guardian mixin ([`f0678ea`](https://github.com/CRM/mis-project-api/commit/f0678eae862ad238782435b263f70c9905c03904))

* Merge pull request &#39;removed passlib, using bcrypt instead&#39; (#16) from bcrypt_instead_passlib into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/16 ([`36a5cf8`](https://github.com/CRM/mis-project-api/commit/36a5cf8cf9dda2788a1f7a6f5325ed1b89b0ecd8))

* removed passlib, using bcrypt instead ([`019c673`](https://github.com/CRM/mis-project-api/commit/019c673ccec5db1dfa7c246039aa4a863a18af83))

* Merge branch &#39;main&#39; of glum.nianmasters.net:CRM/mis-project-api2 ([`31210d4`](https://github.com/CRM/mis-project-api/commit/31210d46c0e514b2fe4ccd7e65f517fe349c9719))

* Merge pull request &#39;some more updates&#39; (#15) from one_more_updates into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/15 ([`c55145b`](https://github.com/CRM/mis-project-api/commit/c55145ba6946806d3196b9b6988ecc13743e2f2c))

* fix module shutdown ([`f70633c`](https://github.com/CRM/mis-project-api/commit/f70633c86cb04b8f7c11a662edf2f97d559ad644))

* some more updates ([`234f760`](https://github.com/CRM/mis-project-api/commit/234f7601111cc2f7244c476edda2e5b5a65bfc9d))

* changes back to normal ([`26c4f68`](https://github.com/CRM/mis-project-api/commit/26c4f68b69767f10a04ab0767a6fb6e55225023d))

* Update pytest.ini ([`0d04375`](https://github.com/CRM/mis-project-api/commit/0d0437557a5e4a8fa7a1eb99c487e6ad8f800b13))

* guardian tests prep ([`a4e7410`](https://github.com/CRM/mis-project-api/commit/a4e7410f2e7b21cb829d61a50f9be2c773232477))

* prepare for notifications tests ([`3de6143`](https://github.com/CRM/mis-project-api/commit/3de6143117f08b5a01d5e11a3ad20a53ffcd63f8))

* Revert &#34;Merge branch &#39;main&#39; into MIS-181-autotests&#34;

This reverts commit d047ddadc53e2c0befae431db633ee642c968f9d, reversing
changes made to a13fe86014ca6690ca03f98f92ccb6619b3b4989. ([`3c10aa3`](https://github.com/CRM/mis-project-api/commit/3c10aa3c2558c7aa30543b45162edc49146a5440))

* Merge branch &#39;main&#39; into MIS-181-autotests ([`d047dda`](https://github.com/CRM/mis-project-api/commit/d047ddadc53e2c0befae431db633ee642c968f9d))

* Merge pull request &#39;updates&#39; (#14) from one_more_updates into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/14 ([`cad7986`](https://github.com/CRM/mis-project-api/commit/cad79864e4368024f8b5201c7c118890146d2c26))

* updates ([`233e528`](https://github.com/CRM/mis-project-api/commit/233e528b9ad2eb016e3216e37d1f0a6416240fee))

* Merge pull request &#39;more_fixes&#39; (#13) from more_fixes into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/13 ([`5eb8103`](https://github.com/CRM/mis-project-api/commit/5eb8103d261ee764ddcb3da408d015b5ca5e3cea))

* Revert &#34;autotest preparing&#34;

This reverts commit c962bc7d4254ff3f5d04bc7a12f6ce5777c12397. ([`b01d88f`](https://github.com/CRM/mis-project-api/commit/b01d88f6b3b508c8b4c584ccabd9555d9285d428))

* resolved merge and revert tests ([`510fe8a`](https://github.com/CRM/mis-project-api/commit/510fe8aaf9b712deed66b520b04e64c2bf06a49f))

* Revert &#34;new structure&#34;

This reverts commit bfe2c5b46b4ca14c500dd69b7a44ef4f18393d76. ([`ce94c09`](https://github.com/CRM/mis-project-api/commit/ce94c095522b97467e14d13363ea70a53e5c1f5c))

* Revert &#34;parametrize introduced&#34;

This reverts commit 273112a627e0122e7376e66d874e3f3ead1835ea. ([`8adac97`](https://github.com/CRM/mis-project-api/commit/8adac979d256334e1f461c3e3f22adf6f587b11e))

* Revert &#34;env setup begin&#34;

This reverts commit 0fa71773af73fca0c73df45822a0a588beff20e1. ([`0071d30`](https://github.com/CRM/mis-project-api/commit/0071d30172d2a9d3bacfc84a2f16f8f71f45d72b))

* Revert &#34;users covered tests&#34;

This reverts commit 791f737154ff3e61836b8a7b90e7d0f0d785205a. ([`e91f899`](https://github.com/CRM/mis-project-api/commit/e91f8992517ea8a20d1b56058496b382ebe2988f))

* Revert &#34;Update conftest.py&#34;

This reverts commit 4bec202acea61d5cb43cdb5c1f0274ef8381eed6. ([`b48ae84`](https://github.com/CRM/mis-project-api/commit/b48ae843f2e11a9a9faff2fcb5f3ec17572bccf3))

* Revert &#34;team tests prepare&#34;

This reverts commit 0d6a5c52beb7044b2bdc32c91180835dccb3356c. ([`2f79613`](https://github.com/CRM/mis-project-api/commit/2f7961364a111e323415763cff19d7d0ce2e69e9))

* Revert &#34;teams covered tests&#34;

This reverts commit f889167c9a9d2a5eafdc8ce363026fdbd652844a. ([`8a7e00e`](https://github.com/CRM/mis-project-api/commit/8a7e00eb9e1f0513664d888fac6d84432ac3b4bb))

* Revert &#34;permissions covered tests&#34;

This reverts commit cd8a4e008f2274843a97d4993b662189623ca93e. ([`0ebb9db`](https://github.com/CRM/mis-project-api/commit/0ebb9db98060c4573529daa11a11c4064d762b01))

* Revert &#34;tests improvements and variables covered&#34;

This reverts commit aac7ffe14a93f7886fea541be6c1d1701bdaa17c. ([`9d299b8`](https://github.com/CRM/mis-project-api/commit/9d299b8b58bb6961a11a6a200da7a1a6df99209f))

* Revert &#34;tests updates&#34;

This reverts commit 2b873e4aa9075dfa370de82f13c61d800f174d00. ([`0563d6c`](https://github.com/CRM/mis-project-api/commit/0563d6c3f8e4b5a25911982ad798675a238bbb53))

* Revert &#34;test case jobs covered&#34;

This reverts commit db60d446ea9135f93e46e3aad3e00c7605b6f738. ([`118da2e`](https://github.com/CRM/mis-project-api/commit/118da2e60c9e89f7f959aa9a6a23a0bc34bd7706))

* Merge pull request &#39;fixes&#39; (#12) from fixes into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/12 ([`29c3687`](https://github.com/CRM/mis-project-api/commit/29c3687d3b7b3bfc2ca5534e181842d0d8a3cad7))

* modules tests covered ([`a13fe86`](https://github.com/CRM/mis-project-api/commit/a13fe86014ca6690ca03f98f92ccb6619b3b4989))

* modules tests prep ([`e0a25ad`](https://github.com/CRM/mis-project-api/commit/e0a25ad9d3f9c09032b01e333ed58064a781194e))

* cleanup ([`f77a6c7`](https://github.com/CRM/mis-project-api/commit/f77a6c7aedbefd4ea6d3a1b24d6647326ea3066d))

* various fixes ([`9c8c759`](https://github.com/CRM/mis-project-api/commit/9c8c759e883346e0a52faea59cf1298bd674725b))

* test case jobs covered ([`db60d44`](https://github.com/CRM/mis-project-api/commit/db60d446ea9135f93e46e3aad3e00c7605b6f738))

* Merge branch &#39;fixes&#39; into MIS-181-autotests ([`1038c08`](https://github.com/CRM/mis-project-api/commit/1038c08ffe540c04eca1facb663c77f1209aacad))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into fixes ([`1831039`](https://github.com/CRM/mis-project-api/commit/18310394f5feb005b60495c07fa9f4f78865d000))

* wip fixes (without merge unify response task) ([`381de53`](https://github.com/CRM/mis-project-api/commit/381de53dcd62e244471c3e2566da5f9f8902679d))

* tests updates ([`2b873e4`](https://github.com/CRM/mis-project-api/commit/2b873e4aa9075dfa370de82f13c61d800f174d00))

* Merge branch &#39;main&#39; into MIS-181-autotests ([`1473b8f`](https://github.com/CRM/mis-project-api/commit/1473b8f4fe62ec7993fe6bcab2ad9d26cfbd340d))

* Merge pull request &#39;MIS-179-Unify-json-response&#39; (#11) from MIS-179-Unify-json-response into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/11 ([`d50a0c7`](https://github.com/CRM/mis-project-api/commit/d50a0c7e4ac4159cac429b73f76c1ac2f189745b))

* small improvements ([`7d36fc3`](https://github.com/CRM/mis-project-api/commit/7d36fc3e6ce02a78baf2ebc0bed7771788747a08))

* tests improvements and variables covered ([`aac7ffe`](https://github.com/CRM/mis-project-api/commit/aac7ffe14a93f7886fea541be6c1d1701bdaa17c))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`131d64b`](https://github.com/CRM/mis-project-api/commit/131d64b07fa049c780eb1a685748970153b9f5c7))

* Merge branch &#39;main&#39; into MIS-179-Unify-json-response ([`2f9ed97`](https://github.com/CRM/mis-project-api/commit/2f9ed975b69a35f2a6cb8b02d41e550832a363e2))

* Merge pull request &#39;various fixes&#39; (#10) from fixes into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/10 ([`59aaae1`](https://github.com/CRM/mis-project-api/commit/59aaae1ee8d963b20e345341f9cace9be630742f))

* Update app.py ([`a822a07`](https://github.com/CRM/mis-project-api/commit/a822a0736b7b93d01c09f5084719736eec214ffc))

* some fixes ([`f39f4ce`](https://github.com/CRM/mis-project-api/commit/f39f4ce54697468dbdd06a213c8ca6bc862ef17b))

* some checks and fixes ([`adb4713`](https://github.com/CRM/mis-project-api/commit/adb471388784d913cbfb2b2cf45462060fa4cfee))

* permissions covered tests ([`cd8a4e0`](https://github.com/CRM/mis-project-api/commit/cd8a4e008f2274843a97d4993b662189623ca93e))

* teams covered tests ([`f889167`](https://github.com/CRM/mis-project-api/commit/f889167c9a9d2a5eafdc8ce363026fdbd652844a))

* Merge branch &#39;main&#39; into MIS-181-autotests ([`5910777`](https://github.com/CRM/mis-project-api/commit/5910777d146f7d97b3beacc189e5c241ab180443))

* Merge pull request &#39;small-patch&#39; (#9) from small-patch into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/9 ([`b3833ad`](https://github.com/CRM/mis-project-api/commit/b3833ad533211a566cc8e7e5e65fce89e424a8ac))

* Update tortoise_manager.py ([`56acd44`](https://github.com/CRM/mis-project-api/commit/56acd44d6db0fcee9cd7a6d0547b465f8ef767dd))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`b375d12`](https://github.com/CRM/mis-project-api/commit/b375d1259983e7ac489e6aac7173213f85340786))

* cleanup and fixes ([`5807949`](https://github.com/CRM/mis-project-api/commit/5807949d6e0f33567065a5fdc9c07c605b643cbf))

* finalize endpoints rework ([`dbe1ab2`](https://github.com/CRM/mis-project-api/commit/dbe1ab2940a33271285c5675af09627dd55c7381))

* team tests prepare ([`0d6a5c5`](https://github.com/CRM/mis-project-api/commit/0d6a5c52beb7044b2bdc32c91180835dccb3356c))

* Update conftest.py ([`4bec202`](https://github.com/CRM/mis-project-api/commit/4bec202acea61d5cb43cdb5c1f0274ef8381eed6))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`3a02279`](https://github.com/CRM/mis-project-api/commit/3a022795f8e778c8b9c2fa276f3c464b4bbdf096))

* merge fix ([`be6bf18`](https://github.com/CRM/mis-project-api/commit/be6bf18c16143690926be6aa2f0106b190cf9724))

* Merge branch &#39;fixes&#39; into MIS-181-autotests ([`bb6802b`](https://github.com/CRM/mis-project-api/commit/bb6802bece6896b0969ff73764e371031c0b6c13))

* various fixes ([`0d40f41`](https://github.com/CRM/mis-project-api/commit/0d40f4194493ae7aa2ae61b9538d5683f21ef432))

* Merge branch &#39;small-patch&#39; into MIS-181-autotests ([`408e744`](https://github.com/CRM/mis-project-api/commit/408e7441db891baa7d3cf473d12d79779c4d5d66))

* tortoise config for create db added ([`9c8ff0b`](https://github.com/CRM/mis-project-api/commit/9c8ff0b9c672df0bf7f48383933a19080c8568c2))

* users covered tests ([`791f737`](https://github.com/CRM/mis-project-api/commit/791f737154ff3e61836b8a7b90e7d0f0d785205a))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`cc79f5c`](https://github.com/CRM/mis-project-api/commit/cc79f5c00bd9e41b8111e26192a03361f1520739))

* Merge branch &#39;main&#39; into MIS-179-Unify-json-response ([`b4ef278`](https://github.com/CRM/mis-project-api/commit/b4ef278c73f74d2a9cea6bbbef8867019384dfee))

* Merge pull request &#39;fix endpoints responses&#39; (#8) from fix_responses into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/8 ([`96d4761`](https://github.com/CRM/mis-project-api/commit/96d4761c56b3dbfcb10e2663906f9ebf33733951))

* fix endpoints responses ([`95e974a`](https://github.com/CRM/mis-project-api/commit/95e974aeafe8d59c960c11db68f2d0e25f78913a))

* Merge branch &#39;main&#39; into MIS-179-Unify-json-response ([`30d0d1d`](https://github.com/CRM/mis-project-api/commit/30d0d1dee051b31a6058b57ec5b94dc356386c6f))

* Merge pull request &#39;using repository and services for auth, module, notification, guardian, task and job endpoints&#39; (#5) from MIS-182-endpoints-services into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/5 ([`0e3989c`](https://github.com/CRM/mis-project-api/commit/0e3989c6d705a80d6dfafe001534a841250c040b))

* using repository and services for auth, module, notification, guardian, task and job endpoints ([`0852937`](https://github.com/CRM/mis-project-api/commit/08529376831f2ebea7d5c15aa4cfd240c4b969de))

* Merge pull request &#39;fix users m2m in GuardianAccessGroup&#39; (#6) from fix_guardian into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/6 ([`0a1ff19`](https://github.com/CRM/mis-project-api/commit/0a1ff19356b2e75987dc46d1f1940d2fd1095453))

* fix users m2m in GuardianAccessGroup ([`f1edca1`](https://github.com/CRM/mis-project-api/commit/f1edca17b7b2317333f9a38fa06020d924509945))

* env setup begin ([`0fa7177`](https://github.com/CRM/mis-project-api/commit/0fa71773af73fca0c73df45822a0a588beff20e1))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`f74abf7`](https://github.com/CRM/mis-project-api/commit/f74abf771179b2b951ec3e4c81ce1484f3669cae))

* fixed shitty typo ([`fc3f8a2`](https://github.com/CRM/mis-project-api/commit/fc3f8a2e8e47b5fcccfd579129072a96d3d106b6))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`5d08338`](https://github.com/CRM/mis-project-api/commit/5d08338438209c1c77189e5c07242d5a8c382c52))

* fixed parameters in exception hamdlers ([`a650d6f`](https://github.com/CRM/mis-project-api/commit/a650d6f7389c160adf2097f0b6cc4a74837bf0b8))

* parametrize introduced ([`273112a`](https://github.com/CRM/mis-project-api/commit/273112a627e0122e7376e66d874e3f3ead1835ea))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`0a92e3a`](https://github.com/CRM/mis-project-api/commit/0a92e3a25a39389eea05b78472467547dee71338))

* refactor ([`1ea45b0`](https://github.com/CRM/mis-project-api/commit/1ea45b007d218eda976f32580ac0c2e00b69c8f1))

* new structure ([`bfe2c5b`](https://github.com/CRM/mis-project-api/commit/bfe2c5b46b4ca14c500dd69b7a44ef4f18393d76))

* Merge branch &#39;MIS-179-Unify-json-response&#39; into MIS-181-autotests ([`eebbfe5`](https://github.com/CRM/mis-project-api/commit/eebbfe56ad1b16bb24987fffa1b26f70fcfbaf8d))

* variables rewrite ([`e9a1f62`](https://github.com/CRM/mis-project-api/commit/e9a1f62815aa899ef4b7d75f5670a7202da2cb09))

* permission rewrite

and fixes ([`4ec8889`](https://github.com/CRM/mis-project-api/commit/4ec88890c43d5698c808ce5fe02848c8a49fbb8a))

* team rewrite

team rewrite
users fix ([`52ffec6`](https://github.com/CRM/mis-project-api/commit/52ffec6b4ccae322d2cc2b37b0d93f752aff79bb))

* users router rewrite

users router rewrite
pagination adapted
exception handler rewrited ([`3f5425e`](https://github.com/CRM/mis-project-api/commit/3f5425e427f7fe418ca89958970fc14d62b1c042))

* Merge branch &#39;main&#39; into MIS-179-Unify-json-response

# Conflicts:
#	core/routes/user.py ([`98eb994`](https://github.com/CRM/mis-project-api/commit/98eb99410d8bc8df55237d061bdf6864830eadaa))

* Merge pull request &#39;repository_and_services&#39; (#4) from repository_and_services into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/4 ([`242c266`](https://github.com/CRM/mis-project-api/commit/242c266c9b38b1970236aaed02eb31ed83cd5e72))

* remove async-timeout ([`4ca4b56`](https://github.com/CRM/mis-project-api/commit/4ca4b56569a312eb6ed22bded155bfaaafc78b50))

* rename services ([`81c04f3`](https://github.com/CRM/mis-project-api/commit/81c04f3789b681e523ef890f86e7955b5907b2a7))

* new requirement fastapi-pagination ([`493db66`](https://github.com/CRM/mis-project-api/commit/493db66b1017c8ebccf0b29853b04d74c60410be))

* repository, unit of work, services ([`4d82335`](https://github.com/CRM/mis-project-api/commit/4d823359eb5f45d3470d368a057c16c1705174f0))

* fixes ([`32a5ec7`](https://github.com/CRM/mis-project-api/commit/32a5ec74a7aba16b30f24ba2544520be7fd8d8b1))

* Merge branch &#39;main&#39; into MIS-179-Unify-json-response ([`9388770`](https://github.com/CRM/mis-project-api/commit/93887708685975ceb1527b67f265d231278225c7))

* start rework ([`198fe69`](https://github.com/CRM/mis-project-api/commit/198fe6987f9033888473e790490827816e18d89f))

* test updates ([`bc2b57c`](https://github.com/CRM/mis-project-api/commit/bc2b57c98f4cf034fb8d3dcbb94a765f2c623158))

* autotest preparing ([`c962bc7`](https://github.com/CRM/mis-project-api/commit/c962bc7d4254ff3f5d04bc7a12f6ce5777c12397))

* Merge pull request &#39;fix migration primary key&#39; (#3) from fix_migration into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/3 ([`1f53cfa`](https://github.com/CRM/mis-project-api/commit/1f53cfa6745958e76c4d1f2d8ddcdd0569acc256))

* fix migration primary key ([`6fe7d82`](https://github.com/CRM/mis-project-api/commit/6fe7d822dca1f9419f65dfa1c41fa356d93f88a6))

* Merge pull request &#39;added manifest.json with information about the module and its dependencies&#39; (#2) from manifest into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/2 ([`479842a`](https://github.com/CRM/mis-project-api/commit/479842ab5d72fe836f09e6634c96e36f079ead6f))

* added manifest.json with information about the module and its dependencies ([`8e86787`](https://github.com/CRM/mis-project-api/commit/8e867878e9691ebafcc14969a10653c23441a68c))

* Merge pull request &#39;guardian&#39; (#1) from guardian into main

Reviewed-on: https://glum.nianmasters.net/CRM/mis-project-api2/pulls/1 ([`dbb3138`](https://github.com/CRM/mis-project-api/commit/dbb31389256d9c9ea99b6092f2af27aa605bc131))

* removed restricted objects ([`53f407b`](https://github.com/CRM/mis-project-api/commit/53f407b8c9f3d464c650ac6466177e2623d7d87a))

* change to guardian access group ([`cd19558`](https://github.com/CRM/mis-project-api/commit/cd19558b042b5b1d82ff086e21cb2b488aa082d3))

* guardian: init setup, access groups, endpoints, migration ([`9ac8c88`](https://github.com/CRM/mis-project-api/commit/9ac8c8886ab32b0d52b4f5d9869334058ea0687c))

* guardian ([`9b4e923`](https://github.com/CRM/mis-project-api/commit/9b4e923e0d953bae6556001c317539b7ad6dfad1))

* fix circular imports; fix namings ([`45d5ab3`](https://github.com/CRM/mis-project-api/commit/45d5ab393f2da34ad68af2c17af636ed43d2cf3e))

* WIP may be broken, fix needed ([`c2233ab`](https://github.com/CRM/mis-project-api/commit/c2233ab073bc76bd4d4b46fb9c5c7ce489611e4d))

* mis project api v2 introduced ([`16f07ae`](https://github.com/CRM/mis-project-api/commit/16f07ae380477be91bc6e436c4e6229f64464130))
